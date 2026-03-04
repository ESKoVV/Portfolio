# ears_overlay.py
import cv2
import numpy as np

_ANIMALS = ["fox", "rabbit", "dog", "wolf", "cat"]

def list_animals():
    return _ANIMALS[:]

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _alpha_blend(dst_bgr, overlay_bgr, alpha_mask):
    """
    dst_bgr: HxWx3 uint8
    overlay_bgr: HxWx3 uint8
    alpha_mask: HxW float32 in [0..1]
    """
    if alpha_mask is None:
        return dst_bgr
    a = alpha_mask[..., None].astype(np.float32)
    dst = dst_bgr.astype(np.float32)
    ov = overlay_bgr.astype(np.float32)
    out = dst * (1.0 - a) + ov * a
    np.clip(out, 0, 255, out)
    return out.astype(np.uint8)

def draw_ears(frame_bgr, face_box, animal="cat", intensity=0.95):
    """
    Рисует ушки на кадре по bbox лица.
    face_box: (x1,y1,x2,y2) в координатах кадра
    animal: fox|rabbit|dog|wolf|cat
    intensity: прозрачность (0..1)
    """
    if animal not in _ANIMALS:
        animal = "cat"

    h, w = frame_bgr.shape[:2]
    x1, y1, x2, y2 = face_box
    x1 = _clamp(int(x1), 0, w-1)
    y1 = _clamp(int(y1), 0, h-1)
    x2 = _clamp(int(x2), 0, w)
    y2 = _clamp(int(y2), 0, h)

    fw = max(1, x2 - x1)
    fh = max(1, y2 - y1)

    # “голова” выше bbox: поднимем верхнюю границу
    head_top_y = int(y1 - 0.35 * fh)
    head_top_y = _clamp(head_top_y, 0, h-1)

    # базовые точки для ушей
    cx = x1 + fw // 2
    left_base  = (int(x1 + 0.28 * fw), int(y1 + 0.05 * fh))
    right_base = (int(x1 + 0.72 * fw), int(y1 + 0.05 * fh))

    # создаём оверлей
    overlay = frame_bgr.copy()
    alpha = np.zeros((h, w), dtype=np.float32)

    def fill_poly(points, color_bgr, a):
        pts = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(overlay, [pts], color_bgr)
        cv2.fillPoly(alpha, [pts], float(a))

    def fill_ellipse(center, axes, angle, color_bgr, a):
        cv2.ellipse(overlay, center, axes, angle, 0, 360, color_bgr, -1, cv2.LINE_AA)
        cv2.ellipse(alpha, center, axes, angle, 0, 360, float(a), -1, cv2.LINE_AA)

    # параметры формы
    ear_h = int(0.55 * fh)
    ear_w = int(0.32 * fw)

    # Цвета (BGR)
    if animal == "fox":
        outer = (40, 90, 230)     # оранжевый
        inner = (160, 180, 255)   # светлый
        tip   = (20, 20, 20)      # тёмный
        style = "pointy"
    elif animal == "rabbit":
        outer = (240, 240, 240)
        inner = (200, 200, 255)
        tip   = (240, 240, 240)
        style = "long"
    elif animal == "dog":
        outer = (60, 80, 120)
        inner = (90, 110, 150)
        tip   = (60, 80, 120)
        style = "floppy"
    elif animal == "wolf":
        outer = (90, 90, 90)
        inner = (140, 140, 140)
        tip   = (40, 40, 40)
        style = "sharp"
    else:  # cat
        outer = (60, 60, 60)
        inner = (120, 120, 120)
        tip   = (30, 30, 30)
        style = "cat"

    a_outer = 0.85 * intensity
    a_inner = 0.75 * intensity

    # helper: треугольное ухо
    def tri_ear(base, direction):
        bx, by = base
        # direction: -1 left, +1 right
        top = (bx + int(direction * 0.08 * fw), head_top_y)
        p1 = (bx - int(0.45 * ear_w), by + int(0.10 * fh))
        p2 = (bx + int(0.45 * ear_w), by + int(0.10 * fh))
        return [p1, top, p2]

    # helper: внутреннее треугольное ухо (меньше)
    def tri_inner(points):
        p1, top, p2 = points
        # сожмём к центру
        def lerp(a, b, t): return (int(a[0] + (b[0]-a[0])*t), int(a[1] + (b[1]-a[1])*t))
        p1i = lerp(p1, top, 0.25)
        p2i = lerp(p2, top, 0.25)
        topi = lerp(top, ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2), 0.15)
        return [p1i, topi, p2i]

    if style in ("pointy", "sharp", "cat"):
        # треугольные уши
        L = tri_ear(left_base, -1)
        R = tri_ear(right_base, +1)

        fill_poly(L, outer, a_outer)
        fill_poly(R, outer, a_outer)

        fill_poly(tri_inner(L), inner, a_inner)
        fill_poly(tri_inner(R), inner, a_inner)

        # тёмные кончики (особенно для fox/wolf)
        if animal in ("fox", "wolf"):
            # маленький треугольник у вершины
            def tip_tri(points):
                p1, top, p2 = points
                t1 = (int(top[0] + 0.15*(p1[0]-top[0])), int(top[1] + 0.18*(p1[1]-top[1])))
                t2 = (int(top[0] + 0.15*(p2[0]-top[0])), int(top[1] + 0.18*(p2[1]-top[1])))
                return [t1, top, t2]
            fill_poly(tip_tri(L), tip, 0.55 * intensity)
            fill_poly(tip_tri(R), tip, 0.55 * intensity)

    elif style == "long":  # rabbit
        # длинные овальные уши
        # центр уха чуть левее/правее от центра головы
        y_center = int(y1 - 0.18 * fh)
        y_center = _clamp(y_center, 0, h-1)
        axes_outer = (int(0.18 * fw), int(0.55 * fh))
        axes_inner = (int(0.11 * fw), int(0.45 * fh))

        # левое
        fill_ellipse((int(cx - 0.20 * fw), y_center), axes_outer, -10, outer, a_outer)
        fill_ellipse((int(cx - 0.20 * fw), y_center + int(0.02 * fh)), axes_inner, -10, inner, a_inner)
        # правое
        fill_ellipse((int(cx + 0.20 * fw), y_center), axes_outer, +10, outer, a_outer)
        fill_ellipse((int(cx + 0.20 * fw), y_center + int(0.02 * fh)), axes_inner, +10, inner, a_inner)

    else:  # floppy dog
        # “висячие” уши: большие эллипсы по бокам
        y_center = int(y1 + 0.15 * fh)
        axes_outer = (int(0.22 * fw), int(0.40 * fh))
        axes_inner = (int(0.14 * fw), int(0.30 * fh))

        fill_ellipse((int(x1 + 0.08 * fw), y_center), axes_outer, 15, outer, a_outer)
        fill_ellipse((int(x1 + 0.08 * fw), y_center + int(0.02 * fh)), axes_inner, 15, inner, a_inner)

        fill_ellipse((int(x2 - 0.08 * fw), y_center), axes_outer, -15, outer, a_outer)
        fill_ellipse((int(x2 - 0.08 * fw), y_center + int(0.02 * fh)), axes_inner, -15, inner, a_inner)

    # Слегка сгладим края (альфа маску)
    alpha_blur = cv2.GaussianBlur(alpha, (0, 0), 1.2)
    return _alpha_blend(frame_bgr, overlay, alpha_blur)