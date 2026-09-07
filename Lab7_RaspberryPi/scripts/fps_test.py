"""Lab 7 - วัดความเร็ว YOLO บน Raspberry Pi (CPU)

ใช้ได้ 2 แบบ
  python3 fps_test.py                       # ใช้กล้อง /dev/video0
  python3 fps_test.py --source ../samples   # ใช้ภาพนิ่งในโฟลเดอร์ (ไม่ต้องมีกล้อง)

ตัวเลข "inference avg" ที่พิมพ์ออกมาตอนจบ คือค่าที่ต้องจดไปกรอกใน
Lab 8 (compare_speed.py) เพื่อเทียบกับ AI HAT

ข้อความ print ต้องเป็น ASCII - console ที่ไม่ใช่ codepage ไทยจะพังถ้าเจอภาษาไทย
และตัวเรนเดอร์ภาพประกอบ (docs/shoot.py) ก็วาดสระ/วรรณยุกต์ไทยไม่ได้
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
        raise SystemExit(f"No image files found in {folder}")
    for i in range(count):
        img = cv2.imread(str(files[i % len(files)]))
        if img is not None:
            yield img


def frames_from_camera(index, count):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise SystemExit(
            f"Cannot open camera index {index}\n"
            "  - list video devices:   ls /dev/video*\n"
            "  - check the USB camera: lsusb\n"
            "  - Pi Camera instead:    rpicam-hello --list-cameras"
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
                    help="camera index (e.g. 0) or a folder of images")
    ap.add_argument("--frames", type=int, default=60, help="frames to measure")
    ap.add_argument("--warmup", type=int, default=5,
                    help="frames to discard first (the first runs are always slow)")
    ap.add_argument("--imgsz", type=int, default=None,
                    help="leave empty to use the size the model was exported at")
    ap.add_argument("--show", action="store_true",
                    help="open a preview window (needs a screen on the Pi, not plain SSH)")
    args = ap.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        raise SystemExit(
            f"Model not found at {model_path}\n"
            "Copy best.onnx from Lab 6 into Lab7_RaspberryPi/model/ first."
        )

    print(f"Model : {model_path}")
    model = YOLO(str(model_path), task="detect")

    total = args.warmup + args.frames
    src = Path(args.source)
    if src.is_dir():
        print(f"Source: folder {src}")
        frames = frames_from_folder(src, total)
    else:
        print(f"Source: camera index {args.source}")
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
            print(f"  measured {len(inf):3d} frames | last inference {inf[-1]:6.1f} ms")

    if args.show:
        cv2.destroyAllWindows()

    if not inf:
        raise SystemExit("Got no frames at all - check the camera or image folder")

    wall = time.perf_counter() - t_start
    per_frame = statistics.mean(pre) + statistics.mean(inf) + statistics.mean(post)
    print()
    print("=" * 58)
    print(f"  frames measured   : {len(inf)} (warmup {args.warmup} discarded)")
    print(f"  preprocess  avg   : {statistics.mean(pre):7.1f} ms")
    print(f"  inference   avg   : {statistics.mean(inf):7.1f} ms   <-- note this for Lab 8")
    print(f"  postprocess avg   : {statistics.mean(post):7.1f} ms")
    print(f"  total per frame   : {per_frame:7.1f} ms")
    print(f"  FPS (model only)  : {1000 / per_frame:7.1f}   = 1000 / {per_frame:.1f}")
    print(f"  FPS (end to end)  : {len(inf) / wall:7.1f}   includes reading each frame")
    print("=" * 58)
    print("  The two FPS lines differ because the first counts only model time,")
    print("  while the second also counts reading frames from disk or camera.")


if __name__ == "__main__":
    main()
