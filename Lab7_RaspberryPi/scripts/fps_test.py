"""Lab 7 - วัดความเร็ว YOLO บน Raspberry Pi (CPU)

ใช้ได้ 2 แบบ
  python3 fps_test.py                 # ใช้กล้อง /dev/video0
  python3 fps_test.py --source ../samples   # ใช้ภาพนิ่งในโฟลเดอร์ (ไม่ต้องมีกล้อง)

ตัวเลข "inference เฉลี่ย (ms)" ที่พิมพ์ออกมาตอนจบ คือค่าที่ต้องจดไปกรอกใน
Lab 8 (compare_speed.py) เพื่อเทียบกับ AI HAT
"""
import argparse
import statistics
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

# อ้างอิงจากตำแหน่งไฟล์นี้เสมอ ไม่ใช่ current directory
# ไม่งั้นรันจากโฟลเดอร์อื่นแล้วหาโมเดลไม่เจอ
HERE = Path(__file__).resolve().parent
DEFAULT_MODEL = HERE.parent / "model" / "best.onnx"

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}


def frames_from_folder(folder, count):
    """วนอ่านภาพนิ่งในโฟลเดอร์ซ้ำไปเรื่อย ๆ จนครบจำนวนที่ขอ"""
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in IMG_EXT)
    if not files:
        raise SystemExit(f"ไม่พบไฟล์ภาพใน {folder}")
    for i in range(count):
        img = cv2.imread(str(files[i % len(files)]))
        if img is not None:
            yield img


def frames_from_camera(index, count):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise SystemExit(
            f"เปิดกล้อง index {index} ไม่ได้\n"
            "  - เช็คว่ามี /dev/video* หรือยัง:  ls /dev/video*\n"
            "  - เช็คว่าระบบเห็นกล้องไหม:      lsusb"
        )
    try:
        for _ in range(count):
            ok, frame = cap.read()
            if not ok:
                break
            yield frame
    finally:
        cap.release()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(DEFAULT_MODEL))
    ap.add_argument("--source", default="0",
                    help="เลข index กล้อง (เช่น 0) หรือ path โฟลเดอร์ภาพ")
    ap.add_argument("--frames", type=int, default=60, help="จำนวนเฟรมที่วัด")
    ap.add_argument("--warmup", type=int, default=5,
                    help="เฟรมแรก ๆ ที่ทิ้งไม่นับ (รอบแรกช้าผิดปกติเสมอ)")
    ap.add_argument("--imgsz", type=int, default=None,
                    help="ปล่อยว่างไว้ = ใช้ขนาดที่ export มา")
    ap.add_argument("--show", action="store_true",
                    help="เปิดหน้าต่างแสดงผล (ต้องรันหน้าจอ Pi ไม่ใช่ผ่าน SSH)")
    args = ap.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        raise SystemExit(
            f"ไม่พบโมเดลที่ {model_path}\n"
            "คัดลอก best.onnx จาก Lab 6 มาไว้ที่ Lab7_RaspberryPi/model/ ก่อน"
        )

    print(f"โมเดล : {model_path}")
    model = YOLO(str(model_path), task="detect")

    total = args.warmup + args.frames
    src = Path(args.source)
    if src.is_dir():
        print(f"แหล่งภาพ: โฟลเดอร์ {src}")
        frames = frames_from_folder(src, total)
    else:
        print(f"แหล่งภาพ: กล้อง index {args.source}")
        frames = frames_from_camera(int(args.source), total)

    predict_kwargs = {"verbose": False}
    if args.imgsz:
        predict_kwargs["imgsz"] = args.imgsz

    pre, inf, post = [], [], []
    t_start = None
    for n, frame in enumerate(frames):
        results = model(frame, **predict_kwargs)
        if n < args.warmup:
            continue                      # ทิ้งรอบอุ่นเครื่อง
        if t_start is None:
            t_start = time.perf_counter()
        speed = results[0].speed          # ultralytics วัดมาให้เป็น ms
        pre.append(speed["preprocess"])
        inf.append(speed["inference"])
        post.append(speed["postprocess"])
        if args.show:
            cv2.imshow("YOLO - Raspberry Pi", results[0].plot())
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        if len(inf) % 10 == 0:
            print(f"  วัดแล้ว {len(inf):3d} เฟรม | inference ล่าสุด {inf[-1]:6.1f} ms")

    if args.show:
        cv2.destroyAllWindows()

    if not inf:
        raise SystemExit("ไม่ได้เฟรมสักเฟรม - เช็คกล้อง/โฟลเดอร์ภาพ")

    wall = time.perf_counter() - t_start
    per_frame = statistics.mean(pre) + statistics.mean(inf) + statistics.mean(post)
    print()
    print("=" * 52)
    print(f"  เฟรมที่วัด        : {len(inf)} (ทิ้งรอบอุ่นเครื่อง {args.warmup})")
    print(f"  preprocess เฉลี่ย : {statistics.mean(pre):7.1f} ms")
    print(f"  inference เฉลี่ย  : {statistics.mean(inf):7.1f} ms   <-- จดตัวนี้ไปใช้ใน Lab 8")
    print(f"  postprocess เฉลี่ย: {statistics.mean(post):7.1f} ms")
    print(f"  รวมต่อเฟรม        : {per_frame:7.1f} ms")
    print(f"  FPS (เฉพาะโมเดล)  : {1000 / per_frame:7.1f}   = 1000 / {per_frame:.1f}")
    print(f"  FPS (ทั้งระบบ)     : {len(inf) / wall:7.1f}   รวมเวลาอ่านภาพเข้ามาด้วย")
    print("=" * 52)
    print("  สองบรรทัดล่างต่างกันเพราะบรรทัดบนนับเฉพาะเวลาที่โมเดลทำงาน")
    print("  ส่วนบรรทัดล่างนับเวลาอ่านภาพจากดิสก์/กล้องเข้าไปด้วย ซึ่งคือของจริง")


if __name__ == "__main__":
    main()
