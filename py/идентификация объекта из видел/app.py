import cv2
import sys

def create_tracker(name: str = "CSRT"):
    name = name.upper()
    legacy = getattr(cv2, "legacy", None)

    def _try(fn):
        try:
            return fn()
        except Exception:
            return None

    # CSRT
    if name == "CSRT":
        if legacy is not None and hasattr(legacy, "TrackerCSRT_create"):
            t = _try(legacy.TrackerCSRT_create)
            if t is not None: return t
        if hasattr(cv2, "TrackerCSRT_create"):
            t = _try(cv2.TrackerCSRT_create)
            if t is not None: return t

    # KCF
    if name == "KCF":
        if legacy is not None and hasattr(legacy, "TrackerKCF_create"):
            t = _try(legacy.TrackerKCF_create)
            if t is not None: return t
        if hasattr(cv2, "TrackerKCF_create"):
            t = _try(cv2.TrackerKCF_create)
            if t is not None: return t

    # MOSSE
    if name == "MOSSE":
        if legacy is not None and hasattr(legacy, "TrackerMOSSE_create"):
            t = _try(legacy.TrackerMOSSE_create)
            if t is not None: return t
        if hasattr(cv2, "TrackerMOSSE_create"):
            t = _try(cv2.TrackerMOSSE_create)
            if t is not None: return t

    raise RuntimeError("Не удалось создать трекер. Установи: pip install opencv-contrib-python")

def main():
    if len(sys.argv) < 2:
        print("Запуск: python app.py <path_to_video> [CSRT|KCF|MOSSE]")
        return

    video_path = sys.argv[1]
    tracker_name = sys.argv[2] if len(sys.argv) >= 3 else "CSRT"

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Не удалось открыть видео: {video_path}")

    win = "Tracker"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    tracker = None
    bbox = None
    paused = False
    last_frame = None

    print("Управление:")
    print("  SPACE  — пауза/плей")
    print("  C      — выбрать объект (лучше на паузе)")
    print("  R      — сбросить трекинг")
    print("  Q/ESC  — выход")

    while True:
        if not paused:
            ok, frame = cap.read()
            if not ok:
                break
            last_frame = frame
        else:
            if last_frame is None:
                ok, frame = cap.read()
                if not ok:
                    break
                last_frame = frame
            frame = last_frame.copy()

        # трекинг
        if tracker is not None and bbox is not None:
            ok, new_box = tracker.update(frame)
            if ok:
                x, y, w, h = map(int, new_box)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"{tracker_name} OK", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, f"{tracker_name} LOST", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        status = "PAUSED" if paused else "PLAY"
        cv2.putText(frame, f"{status} | SPACE pause/play | C select | R reset | Q quit",
                    (10, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow(win, frame)
        key = cv2.waitKey(1) & 0xFF

        if key in (27, ord('q'), ord('Q')):
            break

        if key == ord(' '):
            paused = not paused

        elif key in (ord('r'), ord('R')):
            tracker = None
            bbox = None

        elif key in (ord('c'), ord('C')):
            paused = True
            frame_for_roi = last_frame.copy() if last_frame is not None else frame.copy()

            # ВАЖНО: selectROI использует ТЕКУЩЕЕ окно win
            roi = cv2.selectROI(win, frame_for_roi, fromCenter=False, showCrosshair=True)

            x, y, w, h = map(int, roi)
            if w > 0 and h > 0:
                tracker = create_tracker(tracker_name)
                bbox = (x, y, w, h)
                tracker.init(frame_for_roi, bbox)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()