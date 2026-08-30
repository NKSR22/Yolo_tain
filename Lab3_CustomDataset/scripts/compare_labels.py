"""Lab 3 - เทียบ label ที่นักศึกษาวาดเอง กับเฉลยที่ซ่อนไว้

อ่าน  raw_images/wild_NN.txt   (ผลงานของนักศึกษา)
เทียบ answer_key/wild_NN.txt   (เฉลย)

รายงานให้ทีละรูป: กรอบที่ตรงกัน (พร้อมค่า IoU), วัตถุที่ลืม label,
กรอบที่วาดเกินมา และกรอบที่วาดถูกที่แต่เลือกคลาสผิด

เพิ่ม --images เพื่อวาดภาพเปรียบเทียบ (เฉลย = เขียว, ของเรา = ส้ม) ไว้ที่ compare/
"""
import argparse
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = LAB_DIR / "raw_images"
ANSWER_DIR = LAB_DIR / "answer_key"
COMPARE_DIR = LAB_DIR / "compare"
IOU_MATCH = 0.5          # ต่ำกว่านี้ถือว่าคนละวัตถุ ไม่ใช่แค่วาดเบี้ยว
IOU_GOOD = 0.75          # เกณฑ์ "วาดได้ดี" สำหรับสรุปผล


def read_boxes(path, w, h):
    """อ่านไฟล์ YOLO .txt แล้วแปลงเป็นพิกัดพิกเซล (IoU ต้องคิดบนพิกเซล ไม่ใช่ค่า 0-1
    เพราะแกน x กับ y ถูกหารด้วยตัวเลขคนละตัว)"""
    boxes = []
    if not path.exists():
        return boxes
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        c, cx, cy, bw, bh = int(parts[0]), *(float(v) for v in parts[1:5])
        boxes.append((c, (cx - bw / 2) * w, (cy - bh / 2) * h, (cx + bw / 2) * w, (cy + bh / 2) * h))
    return boxes


def iou(a, b):
    ax1, ay1, ax2, ay2 = a[1:]
    bx1, by1, bx2, by2 = b[1:]
    ix = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    iy = max(0.0, min(ay2, by2) - max(ay1, by1))
    inter = ix * iy
    union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / union if union > 0 else 0.0


def match(answer, student):
    """จับคู่กรอบแบบละโมบ: เลือกคู่ที่ IoU สูงสุดก่อน แล้วตัดออกจากรายการ"""
    scored = sorted(
        ((iou(a, s), ai, si) for ai, a in enumerate(answer) for si, s in enumerate(student)),
        reverse=True,
    )
    pairs, used_a, used_s = [], set(), set()
    for score, ai, si in scored:
        if score < IOU_MATCH or ai in used_a or si in used_s:
            continue
        used_a.add(ai)
        used_s.add(si)
        pairs.append((ai, si, score))
    missed = [i for i in range(len(answer)) if i not in used_a]
    extra = [i for i in range(len(student)) if i not in used_s]
    return pairs, missed, extra


def draw(image_path, answer, student, names, dest):
    from PIL import Image, ImageDraw

    img = Image.open(image_path).convert("RGB")
    d = ImageDraw.Draw(img)
    for c, x1, y1, x2, y2 in answer:
        d.rectangle([x1, y1, x2, y2], outline=(60, 220, 100), width=3)
        d.text((x1 + 4, y1 + 4), f"answer: {names[c]}", fill=(60, 220, 100))
    for c, x1, y1, x2, y2 in student:
        d.rectangle([x1, y1, x2, y2], outline=(255, 150, 40), width=3)
        # วางป้ายไว้ขอบล่าง กันไปทับป้ายของเฉลยตอนที่สองกรอบเกือบซ้อนกันพอดี
        d.text((x1 + 4, min(img.height - 14, y2 - 14)), f"yours: {names[c]}", fill=(255, 150, 40))
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", action="store_true", help="วาดภาพเปรียบเทียบไว้ที่ compare/")
    args = ap.parse_args()

    if not ANSWER_DIR.exists():
        raise SystemExit("No answer_key/ found. Run get_practice_images.bat first.")
    names_file = RAW_DIR / "classes.txt"
    names = [n.strip() for n in names_file.read_text(encoding="utf-8-sig").splitlines() if n.strip()]

    from PIL import Image

    totals = dict(answer=0, student=0, matched=0, good=0, missed=0, extra=0, wrong_class=0)
    ious, unlabelled = [], []

    for img_path in sorted(RAW_DIR.glob("wild_*.jpg")):
        stem = img_path.stem
        student_file = RAW_DIR / f"{stem}.txt"
        answer_file = ANSWER_DIR / f"{stem}.txt"
        if not answer_file.exists():
            continue
        with Image.open(img_path) as im:
            w, h = im.size

        answer = read_boxes(answer_file, w, h)
        student = read_boxes(student_file, w, h)
        totals["answer"] += len(answer)
        totals["student"] += len(student)

        if not student_file.exists():
            unlabelled.append(stem)
            totals["missed"] += len(answer)
            print(f"{stem}: NOT LABELLED YET ({len(answer)} object(s) in the answer key)")
            continue

        pairs, missed, extra = match(answer, student)
        wrong = [(ai, si, s) for ai, si, s in pairs if answer[ai][0] != student[si][0]]
        totals["matched"] += len(pairs)
        totals["good"] += sum(1 for _, _, s in pairs if s >= IOU_GOOD)
        totals["missed"] += len(missed)
        totals["extra"] += len(extra)
        totals["wrong_class"] += len(wrong)
        ious += [s for _, _, s in pairs]

        bits = [f"matched {len(pairs)}/{len(answer)}"]
        if pairs:
            bits.append(f"mean IoU {sum(s for _, _, s in pairs) / len(pairs):.2f}")
        if missed:
            bits.append(f"MISSED {len(missed)} ({', '.join(names[answer[i][0]] for i in missed)})")
        if extra:
            bits.append(f"EXTRA {len(extra)}")
        if wrong:
            bits.append("WRONG CLASS " + ", ".join(
                f"{names[student[si][0]]}->{names[answer[ai][0]]}" for ai, si, _ in wrong))
        print(f"{stem}: " + " | ".join(bits))

        if args.images:
            draw(img_path, answer, student, names, COMPARE_DIR / f"{stem}.jpg")

    print("\n" + "=" * 58)
    print(f"objects in answer key : {totals['answer']}")
    print(f"boxes you drew        : {totals['student']}")
    print(f"matched (IoU >= {IOU_MATCH})  : {totals['matched']}")
    print(f"  of those, tight (>= {IOU_GOOD}): {totals['good']}")
    print(f"missed                : {totals['missed']}")
    print(f"extra boxes           : {totals['extra']}")
    print(f"right box, wrong class: {totals['wrong_class']}")
    if ious:
        print(f"mean IoU of matches   : {sum(ious) / len(ious):.3f}")
    if unlabelled:
        print(f"\nnot labelled yet ({len(unlabelled)}): {', '.join(unlabelled)}")

    print("\nHow to read this:")
    print("  IoU  = how much your box overlaps the answer (1.00 = identical).")
    print("         >= 0.75 is a tight box; 0.50-0.75 means loose or shifted.")
    print("  MISSED      -> you did not draw a box on an object that is there.")
    print("  EXTRA       -> you drew a box where the answer key has nothing.")
    print("  WRONG CLASS -> box is in the right place but the class is wrong.")
    print("\nRerun with --images to write side-by-side pictures into compare/")

    if args.images and COMPARE_DIR.exists():
        print(f"comparison images written to {COMPARE_DIR}")


if __name__ == "__main__":
    main()
