"""Lab 9 - สายพานคัดแยกด้วย YOLO

การแบ่งงาน:
    Raspberry Pi  = กล้อง + YOLO + ตัดสินใจ
    Arduino Uno   = ขับมอเตอร์ + อ่านเซ็นเซอร์ (งานที่ต้องการจังหวะเวลาแน่นอน)

ลำดับการทำงานหนึ่งรอบ:
    1. สายพานเดิน
    2. เซ็นเซอร์เจอวัตถุ -> หยุดสายพาน
    3. ถ่ายภาพแล้วให้ YOLO ทาย
    4. ถ้าเป็นคลาสที่ต้องคัดออก -> สั่งตัวคัดแยกทำงาน
    5. เดินสายพานต่อ

โหมดทดสอบตอนที่ยังไม่มีเซ็นเซอร์:
    python3 conveyor_ai_demo.py --trigger timer --interval 5
ใช้เวลาแทนสัญญาณจากเซ็นเซอร์ ทำให้ไล่ดูตรรกะทั้งวงได้โดยยังไม่ต้องต่อวงจร

ข้อความ print ต้องเป็น ASCII - console ที่ไม่ใช่ codepage ไทยจะพังถ้าเจอภาษาไทย
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

from config import CAMERA_INDEX, MIN_CONFIDENCE, SORT_CLASS
from conveyor_link import ConveyorError, ConveyorLink

# อ้างตำแหน่งจากไฟล์นี้เสมอ ไม่ใช่ current directory
# (สคริปต์เวอร์ชันเก่าใช้ path แบบ relative ที่ชี้ออกนอกรีโปไป 2 ชั้น)
HERE = Path(__file__).resolve().parent
DEFAULT_MODEL = HERE.parent.parent / "Lab7_RaspberryPi" / "model" / "best.onnx"


IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}


class FolderCamera:
    """ป้อนภาพจากโฟลเดอร์แทนกล้อง ใช้ตอนซ้อมตรรกะโดยไม่ต้องมีของจริงวางบนสายพาน

    หน้าตาเหมือน cv2.VideoCapture พอให้ใช้แทนกันได้ในสคริปต์นี้
    """

    def __init__(self, folder):
        self.files = sorted(p for p in Path(folder).iterdir()
                            if p.suffix.lower() in IMG_EXT)
        self.i = 0

    def isOpened(self):
        return bool(self.files)

    def read(self):
        if not self.files:
            return False, None
        path = self.files[self.i % len(self.files)]
        self.i += 1
        return True, cv2.imread(str(path))

    def release(self):
        pass


def classify(model, cap, min_conf):
    """ถ่ายหนึ่งเฟรมแล้วคืน (ชื่อคลาส, ความมั่นใจ) ของวัตถุที่มั่นใจที่สุด"""
    ok, frame = cap.read()
    if not ok or frame is None:
        return None, 0.0

    results = model(frame, verbose=False)
    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        return None, 0.0

    # เรียงตามความมั่นใจ แล้วเอาตัวบนสุด
    best = max(range(len(boxes)), key=lambda i: float(boxes.conf[i]))
    conf = float(boxes.conf[best])
    if conf < min_conf:
        return None, conf
    return model.names[int(boxes.cls[best])], conf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(DEFAULT_MODEL))
    ap.add_argument("--sort-class", default=SORT_CLASS,
                    help="class name that should trigger the sorter")
    ap.add_argument("--min-conf", type=float, default=MIN_CONFIDENCE)
    ap.add_argument("--trigger", choices=("sensor", "timer"), default="sensor",
                    help="'timer' lets you test the whole loop with no sensor wired")
    ap.add_argument("--interval", type=float, default=5.0,
                    help="seconds between cycles when --trigger timer")
    ap.add_argument("--settle", type=float, default=0.3,
                    help="seconds to wait after stopping, so the object stops moving")
    ap.add_argument("--source", default=None,
                    help="folder of images to use instead of the camera, for dry runs")
    args = ap.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Model not found at {model_path}", file=sys.stderr)
        print("Copy best.onnx over from Lab 6 first (see Lab 7 Step 2).", file=sys.stderr)
        return 1

    if args.source:
        cap = FolderCamera(args.source)
        source_name = f"folder {args.source}"
    else:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        source_name = f"camera index {CAMERA_INDEX}"
    if not cap.isOpened():
        print(f"Cannot open {source_name}", file=sys.stderr)
        return 1

    print(f"Model      : {model_path}")
    print(f"Source     : {source_name}")
    print(f"Sort class : {args.sort_class}")
    print(f"Trigger    : {args.trigger}")
    model = YOLO(str(model_path), task="detect")

    sorted_count = seen_count = 0
    try:
        with ConveyorLink() as link:
            print(f"Arduino    : {link.identify()}")
            if args.sort_class not in model.names.values():
                print(f"WARNING: '{args.sort_class}' is not a class this model knows.")
                print(f"         Known classes: {sorted(model.names.values())}")
                print("         The sorter will never fire. Fix SORT_CLASS in config.py.")

            print("Conveyor running. Ctrl+C to stop.")
            link.motor(True)

            while True:
                if args.trigger == "sensor":
                    if not link.wait_for_object(timeout=1.0):
                        continue
                else:
                    time.sleep(args.interval)

                link.motor(False)
                time.sleep(args.settle)      # ให้วัตถุนิ่งก่อนถ่าย

                label, conf = classify(model, cap, args.min_conf)
                seen_count += 1
                if label is None:
                    print(f"  [{seen_count:3d}] nothing confident enough (best {conf:.2f})")
                else:
                    print(f"  [{seen_count:3d}] {label} ({conf:.2f})")
                    if label == args.sort_class:
                        link.sorter(True)
                        time.sleep(1.0)
                        link.sorter(False)
                        sorted_count += 1
                        print(f"        -> sorted out ({sorted_count} so far)")

                link.motor(True)

    except KeyboardInterrupt:
        print()
        print(f"Stopped. Objects seen {seen_count}, sorted out {sorted_count}.")
        return 0
    except ConveyorError as e:
        print("Link error:", e, file=sys.stderr)
        return 1
    finally:
        cap.release()


if __name__ == "__main__":
    sys.exit(main())
