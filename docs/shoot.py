"""shoot.py - เครื่องมือทำภาพประกอบคู่มือ ทุกโหมดเซฟลง docs/images/

    python docs/shoot.py run  <ชื่อ> [-t "หัวข้อ"] -- <คำสั่ง...>   รันคำสั่งแล้วเรนเดอร์ output เป็นภาพ terminal
    python docs/shoot.py text <ชื่อ> -f <ไฟล์log> [-t "หัวข้อ"]     เรนเดอร์ log ที่มีอยู่แล้วเป็นภาพ
    python docs/shoot.py pick <ไฟล์ต้นทาง> <ชื่อ> [-w 900]          ก๊อปภาพผลลัพธ์จาก runs/ มาย่อขนาด
    python docs/shoot.py grab <ส่วนหนึ่งของชื่อหน้าต่าง> <ชื่อ> [-d 8]  นับถอยหลังแล้วจับภาพหน้าต่าง
    python docs/shoot.py clip <ชื่อ>                                 ดึงภาพจาก clipboard (หลังกด Win+Shift+S)

โหมด run/text ไม่ต้องพึ่งคนแคปเลย ใช้ได้กับทุกอย่างที่ผลลัพธ์เป็นข้อความ
เหลือแค่หน้าต่างโปรแกรม GUI ที่ยังต้องใช้ grab/clip
"""
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "images"

# สีให้เข้ากับบล็อกโค้ดในคู่มือ (ดูตัวแปร --code-bg / --code-text ใน manual.html)
BG = "#11141a"
FG = "#c9d1d9"
BAR = "#1d2129"
BAR_FG = "#9aa4b2"
BORDER = "#2a2f3a"

# สีของ ANSI SGR ที่ ultralytics ใช้ -> ให้ตรงกับที่เห็นใน terminal จริง
ANSI = {
    30: "#5c6370", 31: "#e06c75", 32: "#98c379", 33: "#e5c07b",
    34: "#61afef", 35: "#c678dd", 36: "#56b6c2", 37: "#c9d1d9",
    90: "#7f848e", 91: "#e06c75", 92: "#98c379", 93: "#e5c07b",
    94: "#61afef", 95: "#c678dd", 96: "#56b6c2", 97: "#ffffff",
}
SGR = re.compile(r"\x1b\[([0-9;]*)m")
CSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

PAD = 18
LINE_H = 20
BAR_H = 34
FONT_SIZE = 15


def _font(bold=False):
    for name in (("consolab.ttf", "consola.ttf") if bold else ("consola.ttf",)):
        try:
            return ImageFont.truetype(name, FONT_SIZE)
        except OSError:
            continue
    return ImageFont.load_default()


def _clean(text):
    """แปลง output ดิบเป็นบรรทัดที่พร้อมเรนเดอร์

    - \\r ที่ progress bar ใช้เขียนทับ -> เก็บเฉพาะสถานะสุดท้ายของบรรทัดนั้น
    - ลบ escape sequence อื่นที่ไม่ใช่การใส่สี
    """
    lines = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        raw = raw.split("\r")[-1]
        raw = CSI.sub(lambda m: m.group(0) if m.group(0).endswith("m") else "", raw)
        lines.append(raw.rstrip())
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _spans(line):
    """แตกบรรทัดเป็นชิ้น ๆ พร้อมสี/ตัวหนา ตามรหัส ANSI"""
    out, pos, color, bold = [], 0, FG, False
    for m in SGR.finditer(line):
        if m.start() > pos:
            out.append((line[pos:m.start()], color, bold))
        for code in (m.group(1) or "0").split(";"):
            code = int(code or 0)
            if code == 0:
                color, bold = FG, False
            elif code == 1:
                bold = True
            elif code in ANSI:
                color = ANSI[code]
        pos = m.end()
    if pos < len(line):
        out.append((line[pos:], color, bold))
    return out or [("", FG, False)]


def render_text(lines, name, title=None, max_lines=44):
    """วาดข้อความเป็นภาพหน้าต่าง terminal"""
    if len(lines) > max_lines:
        head = max_lines // 2
        tail = max_lines - head - 1
        # ข้อความส่วนนี้ต้องเป็น ASCII เพราะฟอนต์ Consolas ไม่มีสระ/พยัญชนะไทย
        lines = lines[:head] + ["   ... (%d lines omitted) ..." % (len(lines) - head - tail)] + lines[-tail:]

    regular, bold_font = _font(), _font(bold=True)
    probe = Image.new("RGB", (1, 1))
    measure = ImageDraw.Draw(probe)
    width = max(
        (measure.textlength(SGR.sub("", ln), font=regular) for ln in lines),
        default=200,
    )
    W = int(width) + PAD * 2
    W = max(560, min(W, 1180))
    H = BAR_H + PAD + LINE_H * len(lines) + PAD

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, BAR_H], fill=BAR)
    d.line([0, BAR_H, W, BAR_H], fill=BORDER)
    d.rectangle([0, 0, W - 1, H - 1], outline=BORDER)
    if title:
        d.text((PAD, BAR_H // 2 - FONT_SIZE // 2 - 1), title, fill=BAR_FG, font=regular)

    y = BAR_H + PAD
    limit = W - PAD          # ขอบขวาที่ข้อความห้ามเลย
    for line in lines:
        x = PAD
        clipped = False
        for chunk, color, bold in _spans(line):
            if not chunk or clipped:
                continue
            font = bold_font if bold else regular
            if x + d.textlength(chunk, font=font) > limit:
                # ตัดทีละตัวอักษรจนพอดีขอบ แล้วปิดท้ายด้วย … ให้รู้ว่ายังมีต่อ
                while chunk and x + d.textlength(chunk + "…", font=font) > limit:
                    chunk = chunk[:-1]
                chunk += "…"
                clipped = True
            d.text((x, y), chunk, fill=color, font=font)
            x += d.textlength(chunk, font=font)
        y += LINE_H

    return _save(img, name)


def _save(img, name, optimize=True):
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / (name if Path(name).suffix else name + ".png")
    if dest.suffix.lower() in (".jpg", ".jpeg"):
        img.convert("RGB").save(dest, quality=85, optimize=True)
    else:
        img.convert("RGB").save(dest, optimize=optimize)
    print(f"saved {dest}  ({img.width}x{img.height}, {dest.stat().st_size // 1024} KB)")
    return dest


def cmd_run(args):
    if not args.command:
        raise SystemExit("ใส่คำสั่งหลัง -- ด้วย เช่น: shoot.py run demo -- yolo detect predict ...")
    root = Path(__file__).resolve().parent.parent
    command = list(args.command)
    # บน Windows ตัว subprocess หาไฟล์ .exe จาก cwd ของโปรเซสตัวเอง ไม่ใช่จาก cwd= ที่ส่งไป
    # ถ้าคำสั่งแรกเป็น path แบบ relative ที่มีอยู่จริงใน repo ให้แปลงเป็น absolute ก่อน
    candidate = root / command[0]
    if candidate.exists():
        command[0] = str(candidate)

    print("running:", " ".join(command))
    proc = subprocess.run(
        command, capture_output=True, text=True, errors="replace",
        shell=False, cwd=root,
    )
    text = proc.stdout + proc.stderr
    print(f"exit={proc.returncode}, {len(text.splitlines())} lines")
    title = args.title or ("> " + " ".join(args.command))
    render_text(_clean(text), args.name, title, args.max_lines)


def cmd_text(args):
    raw = Path(args.file).read_text(encoding="utf-8", errors="replace")
    render_text(_clean(raw), args.name, args.title, args.max_lines)


def cmd_pick(args):
    img = Image.open(args.src).convert("RGB")
    if img.width > args.width:
        img = img.resize((args.width, round(img.height * args.width / img.width)), Image.LANCZOS)
    _save(img, args.name)


def cmd_clip(args):
    from PIL import ImageGrab

    img = ImageGrab.grabclipboard()
    if img is None:
        raise SystemExit("clipboard ไม่มีภาพ - กด Win+Shift+S แคปก่อนแล้วค่อยรันใหม่")
    if img.width > args.width:
        img = img.resize((args.width, round(img.height * args.width / img.width)), Image.LANCZOS)
    _save(img, args.name)


def cmd_grab(args):
    import ctypes
    from ctypes import wintypes

    from PIL import ImageGrab

    user32 = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            if n:
                buf = ctypes.create_unicode_buffer(n + 1)
                user32.GetWindowTextW(hwnd, buf, n + 1)
                if args.window.lower() in buf.value.lower():
                    found.append((hwnd, buf.value))
        return True

    user32.EnumWindows(cb, 0)
    if not found:
        raise SystemExit(f"ไม่เจอหน้าต่างที่ชื่อมีคำว่า '{args.window}'")
    hwnd, title = found[0]
    print("target:", title)
    for i in range(args.delay, 0, -1):
        print(f"  จับภาพในอีก {i} วินาที ...", flush=True)
        time.sleep(1)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    if img.width > args.width:
        img = img.resize((args.width, round(img.height * args.width / img.width)), Image.LANCZOS)
    _save(img, args.name)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)

    r = sub.add_parser("run", help="รันคำสั่งแล้วเรนเดอร์ output เป็นภาพ terminal")
    r.add_argument("name")
    r.add_argument("-t", "--title")
    r.add_argument("--max-lines", type=int, default=44)
    r.set_defaults(func=cmd_run, command=[])

    t = sub.add_parser("text", help="เรนเดอร์ไฟล์ log เป็นภาพ terminal")
    t.add_argument("name")
    t.add_argument("-f", "--file", required=True)
    t.add_argument("-t", "--title")
    t.add_argument("--max-lines", type=int, default=44)
    t.set_defaults(func=cmd_text)

    p = sub.add_parser("pick", help="ก๊อปภาพผลลัพธ์มาย่อขนาด")
    p.add_argument("src")
    p.add_argument("name")
    p.add_argument("-w", "--width", type=int, default=900)
    p.set_defaults(func=cmd_pick)

    g = sub.add_parser("grab", help="นับถอยหลังแล้วจับภาพหน้าต่าง")
    g.add_argument("window")
    g.add_argument("name")
    g.add_argument("-d", "--delay", type=int, default=8)
    g.add_argument("-w", "--width", type=int, default=1100)
    g.set_defaults(func=cmd_grab)

    c = sub.add_parser("clip", help="ดึงภาพจาก clipboard")
    c.add_argument("name")
    c.add_argument("-w", "--width", type=int, default=1100)
    c.set_defaults(func=cmd_clip)

    # แยกคำสั่งที่อยู่หลัง -- ออกมาเองก่อน ไม่ปล่อยให้ argparse จัดการ
    # (argparse.REMAINDER จะกลืน option ของ shoot.py เข้าไปในคำสั่งด้วย)
    argv = sys.argv[1:]
    after = []
    if "--" in argv:
        i = argv.index("--")
        argv, after = argv[:i], argv[i + 1:]

    args = ap.parse_args(argv)
    if args.mode == "run":
        args.command = after
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
