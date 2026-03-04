import cv2

model = "face_detection_yunet_2023mar.onnx"
cap = cv2.VideoCapture(0)

det = cv2.FaceDetectorYN.create(model, "", (320, 320), score_threshold=0.5, nms_threshold=0.3, top_k=5000)

while True:
    ok, frame = cap.read()
    if not ok: break

    h, w = frame.shape[:2]
    det.setInputSize((w, h))  # важно: под реальный размер кадра

    _, faces = det.detect(frame)  # faces: [x, y, w, h, score, ...]
    if faces is not None:
        for f in faces:
            x, y, bw, bh = map(int, f[:4])
            cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0,0,255), 2)

    cv2.imshow("YuNet", frame)
    k = cv2.waitKey(1) & 0xFF
    if k in (27, ord('q')): break

cap.release()
cv2.destroyAllWindows()
