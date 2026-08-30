"""จับภาพหน้าต่างที่ระบุหลังนับถอยหลัง — ใช้ตอนที่กด Win+Shift+S ไม่ได้
เพราะต้องคาเมาส์ไว้ที่เดิม (เช่น ตอนโชว์เส้น crosshair ใน labelImg)

วิธีใช้:  python docs/capture_window.py labelImg lab3_labelimg_draw [หน่วงวินาที]
"""
import ctypes
import sys
import time
from ctypes import wintypes
from pathlib import Path

from PIL import ImageGrab

OUT = Path(__file__).resolve().parent / "images"
MAX_WIDTH = 1100

user32 = ctypes.windll.user32


def find_window(title_part):
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        if n:
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if title_part.lower() in buf.value.lower():
                found.append((hwnd, buf.value))
        return True

    user32.EnumWindows(cb, 0)
    return found


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: python docs/capture_window.py <window-title-part> <name> [delay]")
    title_part, name = sys.argv[1], sys.argv[2]
    delay = int(sys.argv[3]) if len(sys.argv) > 3 else 8

    wins = find_window(title_part)
    if not wins:
        raise SystemExit(f"No visible window with '{title_part}' in the title.")
    hwnd, title = wins[0]
    print(f"target: {title}")

    for i in range(delay, 0, -1):
        print(f"  capturing in {i}s ...", flush=True)
        time.sleep(1)

    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))

    if img.width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)))
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{name}.png"
    img.convert("RGB").save(dest, optimize=True)
    print(f"saved {dest}  ({img.width}x{img.height}, {dest.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
