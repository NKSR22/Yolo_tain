"""Lab 3 - แก้บั๊กของ labelImg 1.8.6 ให้ทำงานกับ PyQt5 รุ่นใหม่

labelImg 1.8.6 (ออกปี 2021, ไม่มีคนดูแลต่อแล้ว) ส่งค่า float เข้าฟังก์ชันวาดของ Qt
ซึ่ง PyQt5 5.15 ไม่ยอมรับแล้ว ทำให้โปรแกรมเด้งตอนลากกรอบ:

    TypeError: arguments did not match any overloaded call:
      drawLine(self, x1: int, y1: int, x2: int, y2: int)

สคริปต์นี้ครอบค่าเหล่านั้นด้วย int() ให้ รันซ้ำได้ไม่มีผลข้างเคียง
"""
import sys
from pathlib import Path

# (ไฟล์, ข้อความเดิม, ข้อความใหม่)
PATCHES = [
    (
        "canvas.py",
        "p.drawRect(left_top.x(), left_top.y(), rect_width, rect_height)",
        "p.drawRect(int(left_top.x()), int(left_top.y()), int(rect_width), int(rect_height))",
    ),
    (
        "canvas.py",
        "p.drawLine(self.prev_point.x(), 0, self.prev_point.x(), self.pixmap.height())",
        "p.drawLine(int(self.prev_point.x()), 0, int(self.prev_point.x()), int(self.pixmap.height()))",
    ),
    (
        "canvas.py",
        "p.drawLine(0, self.prev_point.y(), self.pixmap.width(), self.prev_point.y())",
        "p.drawLine(0, int(self.prev_point.y()), int(self.pixmap.width()), int(self.prev_point.y()))",
    ),
    (
        "shape.py",
        "painter.drawText(min_x, min_y, self.label)",
        "painter.drawText(int(min_x), int(min_y), self.label)",
    ),
]


def libs_dir():
    try:
        import libs  # labelImg ติดตั้ง package ชื่อ libs ไว้ระดับบนสุดของ site-packages
    except ImportError:
        raise SystemExit("labelImg is not installed. Run install_labelimg.bat first.")
    return Path(libs.__file__).parent


def main():
    root = libs_dir()
    changed = already = 0
    for filename, old, new in PATCHES:
        target = root / filename
        text = target.read_text(encoding="utf-8")
        if new in text:
            already += 1
            continue
        if old not in text:
            print(f"[warn] pattern not found in {filename}, skipping:\n       {old}")
            continue
        target.write_text(text.replace(old, new), encoding="utf-8")
        changed += 1

    print(f"labelImg patched: {changed} fixed, {already} already applied ({root})")
    if changed:
        # ลบ bytecode เก่า ไม่งั้น Python อาจใช้ไฟล์ .pyc เดิม
        for pyc in (root / "__pycache__").glob("*.pyc"):
            pyc.unlink()


if __name__ == "__main__":
    sys.exit(main())
