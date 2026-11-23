"""Lab 0 - โหลดชุดฝึกและเครื่องมือสำหรับ Lab 1-6 ไว้ล่วงหน้า

โหลดครั้งเดียวจบ จะได้ไม่ต้องมานั่งรอดาวน์โหลดพร้อมกันทั้งห้อง
รันซ้ำได้ ของที่มีอยู่แล้วจะถูกข้าม
"""
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# (ชื่อที่แสดง, ขนาดโดยประมาณ, ใช้ใน Lab ไหน)
DATASETS = [
    ("coco8.yaml", "1 MB", "Lab 1"),
    ("african-wildlife.yaml", "100 MB", "Lab 3-6"),
]
WEIGHTS = [("yolo11n.pt", "5 MB", "Lab 1-6")]

results = []


def step(label, fn):
    print(f"\n--- {label} ---", flush=True)
    try:
        detail = fn()
        results.append((True, label, detail or ""))
    except Exception as e:  # noqa: BLE001 - อยากให้ทำข้ออื่นต่อแม้ข้อนี้พัง
        print(f"FAILED: {e}")
        traceback.print_exc(limit=1)
        results.append((False, label, str(e)[:70]))


def get_weights(name):
    from ultralytics import YOLO

    YOLO(name)  # โหลดไฟล์ .pt ให้เองถ้ายังไม่มี
    return name


def get_dataset(name):
    from ultralytics.data.utils import check_det_dataset

    info = check_det_dataset(name)
    train = Path(info["train"])
    n = len(list(train.glob("*.jpg"))) + len(list(train.glob("*.png")))
    return f"{n} train images at {info['path']}"


def get_lab2_samples():
    sys.path.insert(0, str(ROOT / "Lab2_Inference" / "scripts"))
    import get_samples

    get_samples.download_images()
    get_samples.make_video()
    return "Lab2_Inference/samples ready"


def get_labelimg():
    import subprocess

    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "labelImg"], check=True)
    subprocess.run([sys.executable, str(ROOT / "Lab3_CustomDataset/scripts/patch_labelimg.py")], check=True)
    return "installed and patched"


def main():
    print("=" * 62)
    print(" Prefetching practice assets for Labs 1-6 (run this before class)")
    print(" Downloads vary depending on what is already cached. Re-running is safe.")
    print("=" * 62)

    for name, size, labs in WEIGHTS:
        step(f"{name} ({size}, {labs})", lambda n=name: get_weights(n))
    for name, size, labs in DATASETS:
        step(f"{name} ({size}, {labs})", lambda n=name: get_dataset(n))
    step("Lab 2 sample image/video", get_lab2_samples)
    step("labelImg for Lab 3", get_labelimg)

    print("\n" + "=" * 62)
    ok = sum(1 for good, _, _ in results if good)
    for good, label, detail in results:
        print(f"  [{'OK  ' if good else 'FAIL'}] {label}" + (f"  - {detail}" if detail else ""))
    print("=" * 62)
    print(f"{ok}/{len(results)} ready")
    if ok < len(results):
        print("\nRe-run this script when you have a stable connection.")
        print("Anything still failing on the day is downloadable in class, just slower.")
        return 1
    print("\nAll set - you can start the labs offline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
