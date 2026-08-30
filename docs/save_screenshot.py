"""บันทึกภาพที่อยู่ใน clipboard ลง docs/images/ (ใช้คู่กับการกด Win+Shift+S)

วิธีใช้:  python docs/save_screenshot.py lab2_webcam
"""
import sys
from pathlib import Path

from PIL import ImageGrab

OUT = Path(__file__).resolve().parent / "images"
MAX_WIDTH = 1100


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python docs/save_screenshot.py <name-without-extension>")
    name = sys.argv[1]

    img = ImageGrab.grabclipboard()
    if img is None:
        raise SystemExit("No image in the clipboard. Press Win+Shift+S, take the snip, then run this again.")

    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)))
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{name}.png"
    img.convert("RGB").save(dest, optimize=True)
    print(f"saved {dest}  ({img.width}x{img.height}, {dest.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
