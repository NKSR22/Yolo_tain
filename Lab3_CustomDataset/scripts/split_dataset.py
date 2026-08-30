"""Lab 3 - แบ่งภาพที่ label แล้วเป็น train/val และเขียน data.yaml ให้อัตโนมัติ

อ่านจาก  Lab3_CustomDataset/raw_images/  (ภาพ + ไฟล์ .txt ที่ labelImg สร้าง + classes.txt)
เขียนไป  Lab3_CustomDataset/dataset/     (images/labels แยก train/val + data.yaml)
"""
import random
import shutil
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = LAB_DIR / "raw_images"
DATASET_DIR = LAB_DIR / "dataset"
CLASSES_FILE = RAW_DIR / "classes.txt"
VAL_RATIO = 0.2
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp")


def read_classes():
    if not CLASSES_FILE.exists():
        print(f"WARNING: {CLASSES_FILE.name} not found, falling back to a single class 'object'")
        return ["object"]
    # utf-8-sig: Notepad บางรุ่นเซฟไฟล์พร้อม BOM ถ้าอ่านแบบ utf-8 เฉย ๆ คลาสแรกจะกลายเป็น "﻿person"
    names = [line.strip() for line in CLASSES_FILE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not names:
        print(f"WARNING: {CLASSES_FILE.name} is empty, falling back to a single class 'object'")
        return ["object"]
    return names


def clear_previous_split():
    """ลบผลการแบ่งรอบก่อน เพื่อไม่ให้ภาพเก่าที่ลบไปแล้วค้างอยู่ใน dataset"""
    for split in ("train", "val"):
        for kind in ("images", "labels"):
            d = DATASET_DIR / kind / split
            d.mkdir(parents=True, exist_ok=True)
            for f in d.iterdir():
                if f.is_file():
                    f.unlink()


def write_data_yaml(names):
    # ไม่ใส่คีย์ "path:" โดยตั้งใจ - Ultralytics resolve path แบบ relative จาก
    # datasets_dir ส่วนกลาง ไม่ใช่จากที่ตั้งของไฟล์นี้ ถ้าไม่มี path มันจะอิงไฟล์นี้แทน
    names_line = ", ".join(f"'{n}'" for n in names)
    (DATASET_DIR / "data.yaml").write_text(
        f"train: images/train\nval: images/val\n\nnc: {len(names)}\nnames: [{names_line}]\n",
        encoding="utf-8",
    )


def main():
    if not RAW_DIR.exists():
        print(f"{RAW_DIR} not found. Run make_dataset_structure.bat first.")
        return
    images = sorted(p for p in RAW_DIR.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    if not images:
        print("No images found in raw_images/. Put your photos there and label them first.")
        return

    names = read_classes()
    random.seed(42)
    random.shuffle(images)
    n_val = max(1, int(len(images) * VAL_RATIO))
    val_set = set(images[:n_val])

    clear_previous_split()
    unlabeled = []
    for img_path in images:
        label_path = img_path.with_suffix(".txt")
        split = "val" if img_path in val_set else "train"
        shutil.copy(img_path, DATASET_DIR / "images" / split / img_path.name)
        if label_path.exists():
            shutil.copy(label_path, DATASET_DIR / "labels" / split / label_path.name)
        else:
            unlabeled.append(img_path.name)

    write_data_yaml(names)

    print(f"Done. train={len(images) - n_val} val={n_val}")
    print(f"Classes ({len(names)}): {', '.join(names)}")
    if unlabeled:
        print(f"WARNING: {len(unlabeled)} image(s) have no .txt label and will count as background:")
        for name in unlabeled[:10]:
            print(f"  - {name}")
        if len(unlabeled) > 10:
            print(f"  ... and {len(unlabeled) - 10} more")
    print(f"data.yaml written to {DATASET_DIR / 'data.yaml'}")


if __name__ == "__main__":
    main()
