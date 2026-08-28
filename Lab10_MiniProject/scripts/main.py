import csv
import time
from pathlib import Path
import cv2
from ultralytics import YOLO

MODEL_PATH = Path(__file__).parent.parent / "model" / "best.onnx"
LOG_PATH = Path(__file__).parent.parent / "logs" / "session.csv"
CAMERA_INDEX = 0

def main():
    LOG_PATH.parent.mkdir(exist_ok=True)
    model = YOLO(str(MODEL_PATH))
    cap = cv2.VideoCapture(CAMERA_INDEX)

    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "class", "confidence"])
        print("Mini project running. Ctrl+C to stop.")
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                results = model(frame, verbose=False)
                for box in results[0].boxes:
                    cls_name = model.names[int(box.cls[0])]
                    conf = float(box.conf[0])
                    writer.writerow([time.time(), cls_name, f"{conf:.3f}"])
                    print(f"{cls_name} ({conf:.2f})")
                    # TODO: เรียกฟังก์ชันควบคุม GPIO/Sorter ตามคลาสที่ตรวจพบ (ดู Lab 9)
                annotated = results[0].plot()
                cv2.imshow("Mini Project", annotated)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
