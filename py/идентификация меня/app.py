import os
import cv2
import numpy as np
from ears_overlay import draw_ears

MODEL_PATH = "face_detection_yunet_2023mar.onnx"
MARKER_IMG_FILE = "target_marker.png"

# --- Face tracking ---
IOU_WEIGHT = 0.55
HIST_WEIGHT = 0.45
SWITCH_MIN_SCORE = 0.40
HOLD_FRAMES_AFTER_LOSS = 12
FACE_PADDING = 0.08

# --- Marker reacquire (template matching) ---
TM_METHOD = cv2.TM_CCOEFF_NORMED
TM_THRESHOLD = 0.62          # если маркер контрастный -> 0.65..0.75
TM_SEARCH_DOWNSCALE = 0.75   # 0.5..1.0 (меньше = быстрее)

# --- Marker capture size when clicking (manual marker mode) ---
MARKER_BOX_SIZE_FRAC = 0.12  # 12% от меньшей стороны кадра

# --- Auto marker from face click (chest/cloth below face) ---
AUTO_MARKER_HEIGHT_MULT = 1.35  # высота области под лицом (в долях высоты лица)
AUTO_MARKER_RESIZE = 200        # маркер приводим к 200x200 для matchTemplate

# --- Global state ---
selected_box = None          # (x1,y1,x2,y2)
selected_hist = None
lost_counter = 0

marker_patch = None          # BGR patch

fullscreen = False
mirror = False               # по умолчанию без зеркала
ear_type = "cat"             # fox|rabbit|dog|wolf|cat

CLICK_SELECT_FACE = 0
CLICK_SELECT_MARKER = 1
click_mode = CLICK_SELECT_FACE


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def expand_box(box, w, h, pad=0.08):
    x1, y1, x2, y2 = box
    bw, bh = (x2 - x1), (y2 - y1)
    px, py = int(bw * pad), int(bh * pad)
    return (
        clamp(int(x1 - px), 0, w - 1),
        clamp(int(y1 - py), 0, h - 1),
        clamp(int(x2 + px), 0, w),
        clamp(int(y2 + py), 0, h),
    )


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1, (bx2 - bx1) * (by2 - by1))
    return inter / float(area_a + area_b - inter + 1e-9)


def compute_hist(frame_bgr, box):
    x1, y1, x2, y2 = box
    roi = frame_bgr[y1:y2, x1:x2]
    if roi.size == 0:
        return None
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    return hist


def hist_sim(h1, h2):
    if h1 is None or h2 is None:
        return 0.0
    s = cv2.compareHist(h1, h2, cv2.HISTCMP_CORREL)  # [-1..1]
    return float((s + 1.0) * 0.5)  # -> [0..1]


def detect_faces(det, frame_bgr):
    h, w = frame_bgr.shape[:2]
    det.setInputSize((w, h))
    _, faces = det.detect(frame_bgr)
    boxes = []
    if faces is None:
        return boxes
    for f in faces:
        x, y, bw, bh = f[:4]
        x1 = clamp(int(x), 0, w - 1)
        y1 = clamp(int(y), 0, h - 1)
        x2 = clamp(int(x + bw), 0, w)
        y2 = clamp(int(y + bh), 0, h)
        if (x2 - x1) >= 12 and (y2 - y1) >= 12:
            boxes.append((x1, y1, x2, y2))
    return boxes


def face_center(b):
    return ((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)


def nearest_face_to_point(faces, px, py):
    return min(faces, key=lambda b: (face_center(b)[0] - px) ** 2 + (face_center(b)[1] - py) ** 2)


def save_marker(patch_bgr):
    cv2.imwrite(MARKER_IMG_FILE, patch_bgr)
    print(f"[marker] saved -> {MARKER_IMG_FILE}")


def load_marker():
    global marker_patch
    if os.path.exists(MARKER_IMG_FILE):
        img = cv2.imread(MARKER_IMG_FILE)
        if img is not None and img.size > 0:
            marker_patch = img
            print(f"[marker] loaded <- {MARKER_IMG_FILE}")


def find_marker(frame_bgr):
    """Return (mx,my,score) center in original frame coords, or None."""
    global marker_patch
    if marker_patch is None:
        return None

    if TM_SEARCH_DOWNSCALE != 1.0:
        small = cv2.resize(
            frame_bgr, None,
            fx=TM_SEARCH_DOWNSCALE, fy=TM_SEARCH_DOWNSCALE,
            interpolation=cv2.INTER_AREA
        )
        templ = cv2.resize(
            marker_patch, None,
            fx=TM_SEARCH_DOWNSCALE, fy=TM_SEARCH_DOWNSCALE,
            interpolation=cv2.INTER_AREA
        )
    else:
        small = frame_bgr
        templ = marker_patch

    sh, sw = small.shape[:2]
    th, tw = templ.shape[:2]
    if th >= sh or tw >= sw:
        return None

    res = cv2.matchTemplate(small, templ, TM_METHOD)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val < TM_THRESHOLD:
        return None

    cx = max_loc[0] + tw // 2
    cy = max_loc[1] + th // 2

    if TM_SEARCH_DOWNSCALE != 1.0:
        cx = int(cx / TM_SEARCH_DOWNSCALE)
        cy = int(cy / TM_SEARCH_DOWNSCALE)

    return (cx, cy, float(max_val))


def toggle_fullscreen(win="Webcam"):
    global fullscreen
    fullscreen = not fullscreen
    cv2.setWindowProperty(
        win,
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL
    )


def extract_auto_marker(frame_bgr, face_box):
    """
    Берём область НИЖЕ лица (одежда/грудь/бейдж) — НЕ лицо.
    Возвращает patch 200x200 или None.
    """
    h, w = frame_bgr.shape[:2]
    x1, y1, x2, y2 = face_box
    fh = y2 - y1

    mx1 = clamp(x1, 0, w - 1)
    mx2 = clamp(x2, 0, w)
    my1 = clamp(y2, 0, h - 1)
    my2 = clamp(y2 + int(AUTO_MARKER_HEIGHT_MULT * fh), 0, h)

    if (mx2 - mx1) < 12 or (my2 - my1) < 12:
        return None

    patch = frame_bgr[my1:my2, mx1:mx2].copy()
    if patch.size == 0:
        return None

    patch = cv2.resize(patch, (AUTO_MARKER_RESIZE, AUTO_MARKER_RESIZE), interpolation=cv2.INTER_AREA)
    return patch


def on_mouse(event, x, y, flags, param):
    """
    param = (frame_bgr, faces, w, h)
    """
    global selected_box, selected_hist, lost_counter
    global marker_patch, click_mode

    if event != cv2.EVENT_LBUTTONDOWN:
        return

    frame_bgr, faces, w, h = param

    if click_mode == CLICK_SELECT_FACE:
        if not faces:
            return

        # выбрать ближайшее лицо
        b = nearest_face_to_point(faces, x, y)
        b = expand_box(b, w, h, FACE_PADDING)

        selected_box = b
        selected_hist = compute_hist(frame_bgr, b)
        lost_counter = 0

        # ✅ ВАЖНО: после каждого клика сохраняем МАРКЕР (одежда/грудь ниже лица)
        auto_patch = extract_auto_marker(frame_bgr, b)
        if auto_patch is not None:
            marker_patch = auto_patch
            save_marker(marker_patch)

    else:
        # MARKER mode: сохраняем квадрат вокруг клика как маркер (ручной вариант)
        size = int(min(w, h) * MARKER_BOX_SIZE_FRAC)
        x1 = clamp(x - size // 2, 0, w - 1)
        y1 = clamp(y - size // 2, 0, h - 1)
        x2 = clamp(x + size // 2, 0, w)
        y2 = clamp(y + size // 2, 0, h)

        patch = frame_bgr[y1:y2, x1:x2].copy()
        if patch.size == 0:
            return

        patch = cv2.resize(patch, (AUTO_MARKER_RESIZE, AUTO_MARKER_RESIZE), interpolation=cv2.INTER_AREA)
        marker_patch = patch
        save_marker(marker_patch)
        print("[marker] captured manually (MARKER mode)")


def main():
    global selected_box, selected_hist, lost_counter
    global mirror, ear_type, click_mode

    load_marker()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Не удалось открыть вебкамеру (VideoCapture(0)).")

    det = cv2.FaceDetectorYN.create(
        MODEL_PATH, "", (320, 320),
        score_threshold=0.55, nms_threshold=0.3, top_k=5000
    )

    cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if mirror:
            frame = cv2.flip(frame, 1)

        h, w = frame.shape[:2]
        faces = detect_faces(det, frame)

        # callback каждый кадр (нужны свежие frame/faces)
        cv2.setMouseCallback("Webcam", on_mouse, (frame, faces, w, h))

        # --- 1) Tracking выбранного лица ---
        if selected_box is not None:
            best_score = 0.0
            best_box = None

            for b in faces:
                eb = expand_box(b, w, h, FACE_PADDING)
                s_iou = iou(selected_box, eb)
                s_hist = hist_sim(selected_hist, compute_hist(frame, eb))
                score = IOU_WEIGHT * s_iou + HIST_WEIGHT * s_hist
                if score > best_score:
                    best_score = score
                    best_box = eb

            if best_box is not None and best_score >= SWITCH_MIN_SCORE:
                selected_box = best_box
                new_hist = compute_hist(frame, best_box)
                if new_hist is not None and selected_hist is not None:
                    selected_hist = 0.85 * selected_hist + 0.15 * new_hist
                elif new_hist is not None:
                    selected_hist = new_hist
                lost_counter = 0
            else:
                lost_counter += 1
                if lost_counter > HOLD_FRAMES_AFTER_LOSS:
                    selected_box = None
                    selected_hist = None
                    lost_counter = 0

        # --- 2) Автоподхват по маркеру, если потерялись ---
        if selected_box is None and marker_patch is not None and faces:
            found = find_marker(frame)
            if found is not None:
                mx, my, score = found

                # debug: точка маркера
                cv2.circle(frame, (mx, my), 8, (255, 255, 0), -1)
                cv2.putText(frame, f"marker {score:.2f}", (mx + 10, my),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                best = nearest_face_to_point(faces, mx, my)
                selected_box = expand_box(best, w, h, FACE_PADDING)
                selected_hist = compute_hist(frame, selected_box)

        # --- Рисуем лица ---
        for b in faces:
            eb = expand_box(b, w, h, FACE_PADDING)
            color = (0, 0, 255)
            thick = 2
            if selected_box is not None and iou(selected_box, eb) > 0.5:
                color = (0, 255, 0)
                thick = 3
            cv2.rectangle(frame, (eb[0], eb[1]), (eb[2], eb[3]), color, thick)

        # --- Ушки на выбранном ---
        if selected_box is not None:
            frame = draw_ears(frame, selected_box, animal=ear_type, intensity=0.95)

        # UI
        mode_txt = "FACE" if click_mode == CLICK_SELECT_FACE else "MARKER"
        cv2.putText(
            frame,
            f"Click:{mode_txt} | TAB switch | 1-fox 2-rabbit 3-dog 4-wolf 5-cat | F full | M mirror | R reset | Q quit",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.imshow("Webcam", frame)
        key = cv2.waitKey(1) & 0xFF

        # Hotkeys
        if key in (27, ord('q'), ord('Q')):
            break
        elif key in (ord('f'), ord('F')):
            toggle_fullscreen("Webcam")
        elif key in (ord('m'), ord('M')):
            mirror = not mirror
        elif key == 9:  # TAB
            click_mode = CLICK_SELECT_MARKER if click_mode == CLICK_SELECT_FACE else CLICK_SELECT_FACE
        elif key in (ord('r'), ord('R')):
            selected_box = None
            selected_hist = None
            lost_counter = 0
        elif key == ord('1'):
            ear_type = "fox"
        elif key == ord('2'):
            ear_type = "rabbit"
        elif key == ord('3'):
            ear_type = "dog"
        elif key == ord('4'):
            ear_type = "wolf"
        elif key == ord('5'):
            ear_type = "cat"

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()