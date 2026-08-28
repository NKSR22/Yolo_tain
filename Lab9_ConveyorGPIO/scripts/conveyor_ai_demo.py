import time
import cv2
from gpiozero import Motor, DigitalInputDevice, OutputDevice
from ultralytics import YOLO
from config import (MOTOR_IN1, MOTOR_IN2, MOTOR_ENABLE, SENSOR_PIN,
                     SORTER_PIN, CAMERA_INDEX)

MODEL_PATH = "../../Lab6_Export/../Lab4_TrainTuning/runs/exp/weights/best.onnx"
SORT_CLASS = "defect"  # เปลี่ยนเป็นชื่อคลาสที่ต้องการให้ sorter ทำงานเมื่อพบ

motor = Motor(forward=MOTOR_IN1, backward=MOTOR_IN2, enable=MOTOR_ENABLE)
sensor = DigitalInputDevice(SENSOR_PIN)
sorter = OutputDevice(SORTER_PIN)
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(CAMERA_INDEX)


def classify_object():
    ok, frame = cap.read()
    if not ok:
        return None
    results = model(frame, verbose=False)
    boxes = results[0].boxes
    if len(boxes) == 0:
        return None
    cls_id = int(boxes.cls[0])
    return model.names[cls_id]


def main():
    print("Conveyor AI sorting demo started. Ctrl+C to stop.")
    motor.forward()
    try:
        while True:
            if sensor.is_active:
                motor.stop()
                time.sleep(0.3)  # ให้วัตถุนิ่งก่อนถ่ายภาพ
                label = classify_object()
                print(f"Detected: {label}")
                if label == SORT_CLASS:
                    sorter.on()
                    time.sleep(1)
                    sorter.off()
                motor.forward()
            time.sleep(0.05)
    except KeyboardInterrupt:
        motor.stop()
        cap.release()
        print("Stopped.")


if __name__ == "__main__":
    main()
