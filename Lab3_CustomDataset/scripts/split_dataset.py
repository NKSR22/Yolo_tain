import random
import shutil
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "raw_images"
DATASET_DIR = Path(__file__).parent.parent / "dataset"
VAL_RATIO = 0.2

def main():
    images = sorted([p for p in RAW_DIR.glob("*.*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    if not images:
        print("No images found in raw_images/. Label your images there first (image + .txt pairs).")
        return
    random.seed(42)
    random.shuffle(images)
    n_val = max(1, int(len(images) * VAL_RATIO))
    val_set = set(images[:n_val])

    for img_path in images:
        label_path = img_path.with_suffix(".txt")
        split = "val" if img_path in val_set else "train"
        shutil.copy(img_path, DATASET_DIR / "images" / split / img_path.name)
        if label_path.exists():
            shutil.copy(label_path, DATASET_DIR / "labels" / split / label_path.name)
        else:
            print(f"WARNING: no label file for {img_path.name}")

    print(f"Done. train={len(images)-n_val} val={n_val}")

if __name__ == "__main__":
    main()
