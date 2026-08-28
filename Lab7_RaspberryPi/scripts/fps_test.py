import time
import cv2
from ultralytics import YOLO

model = YOLO("../model/best.onnx")
cap = cv2.VideoCapture(0)

frame_count = 0
t0 = time.time()
while True:
    ok, frame = cap.read()
    if not ok:
        break
    results = model(frame, imgsz=320, verbose=False)
    annotated = results[0].plot()
    frame_count += 1
    if frame_count % 30 == 0:
        fps = frame_count / (time.time() - t0)
        print(f"FPS: {fps:.1f}")
    cv2.imshow("YOLO - Raspberry Pi", annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
