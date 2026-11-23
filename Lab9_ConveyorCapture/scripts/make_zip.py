"""Pack captured_images/<class>/*.jpg into conveyor_images.zip for Lab 10 on Colab."""

import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "captured_images"
TARGET = HERE.parent / "conveyor_images.zip"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


def main():
    classes = sorted(p for p in SOURCE.iterdir() if p.is_dir()) if SOURCE.is_dir() else []
    counts = {}
    with zipfile.ZipFile(TARGET, "w", zipfile.ZIP_DEFLATED) as archive:
        for folder in classes:
            images = sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
            for image in images:
                # Forward slashes, one folder per class: the layout Lab 10 expects.
                archive.write(image, f"{folder.name}/{image.name}")
            if images:
                counts[folder.name] = len(images)

    if not counts:
        TARGET.unlink()
        print(f"[ERROR] No images found under {SOURCE}")
        print("        Capture some with run_capture_gui.bat first.")
        return 1

    for name, count in counts.items():
        print(f"  {name:<20} {count:>5} images")
    print(f"  {'total':<20} {sum(counts.values()):>5} images")
    print(f"Wrote {TARGET} ({TARGET.stat().st_size / 1e6:.1f} MB)")
    print("Upload it to the top level of My Drive, then open Lab 10.")
    if len(counts) < 2:
        print("[WARN] Only one class. YOLO still trains, but it learns nothing to tell apart.")
    if min(counts.values()) < 30:
        print("[WARN] A class has fewer than 30 images. Aim for 50+ per class.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
