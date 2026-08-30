"""Lab 3 - ดึงรูปสำหรับฝึก label พร้อมเก็บเฉลยแยกไว้

ดึงรูปจากชุด african-wildlife (ชุดเดียวกับที่จะใช้เทรนใน Lab 4) มาวางใน raw_images/
โดย **ย้ายไฟล์เฉลยไปเก็บไว้ที่ answer_key/** เพื่อให้ฝึก label เองก่อน
แล้วค่อยรัน compare_labels.py เทียบผลงานกับเฉลยทีหลัง

ถ้ายังไม่มี dataset ในเครื่อง Ultralytics จะดาวน์โหลดให้เอง (~100 MB ครั้งเดียว)
"""
import random
import shutil
from collections import defaultdict
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = LAB_DIR / "raw_images"
ANSWER_DIR = LAB_DIR / "answer_key"
N_IMAGES = 20
SEED = 3  # คงที่ เพื่อให้ทุกคนได้รูปชุดเดียวกันและเทียบกับคู่มือได้


def load_dataset():
    from ultralytics.data.utils import check_det_dataset

    print("Preparing the african-wildlife dataset (first run downloads ~100 MB)")
    return check_det_dataset("african-wildlife.yaml")


def pick_balanced(pairs, names, n):
    """เลือกรูปให้กระจายครบทุกคลาส แทนที่จะสุ่มล้วน ๆ ซึ่งอาจได้คลาสเดียวซ้ำ ๆ"""
    by_class = defaultdict(list)
    for img, lab in pairs:
        classes = {int(line.split()[0]) for line in lab.read_text().splitlines() if line.strip()}
        for c in classes:
            by_class[c].append((img, lab))

    rng = random.Random(SEED)
    for items in by_class.values():
        rng.shuffle(items)

    picked, seen = [], set()
    order = sorted(by_class)
    while len(picked) < n:
        added = False
        for c in order:                      # วนหยิบทีละคลาสสลับกันไป
            while by_class[c]:
                img, lab = by_class[c].pop()
                if img.name in seen:
                    continue
                seen.add(img.name)
                picked.append((img, lab))
                added = True
                break
            if len(picked) >= n:
                break
        if not added:
            break
    return picked


def main():
    data = load_dataset()
    names = data["names"]
    src_img = Path(data["path"]) / "images" / "test"
    src_lab = Path(data["path"]) / "labels" / "test"
    if not src_img.exists():                 # บางชุดไม่มี test ให้ใช้ val แทน
        src_img = Path(data["val"])
        src_lab = Path(str(src_img).replace("images", "labels"))

    pairs = [(p, src_lab / (p.stem + ".txt")) for p in sorted(src_img.glob("*.jpg"))]
    pairs = [(i, l) for i, l in pairs if l.exists()]
    if not pairs:
        raise SystemExit(f"No image/label pairs found in {src_img}")

    picked = pick_balanced(pairs, names, N_IMAGES)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ANSWER_DIR.mkdir(parents=True, exist_ok=True)
    for f in list(RAW_DIR.glob("wild_*.jpg")) + list(ANSWER_DIR.glob("wild_*.txt")):
        f.unlink()

    counts = defaultdict(int)
    for i, (img, lab) in enumerate(picked, start=1):
        stem = f"wild_{i:02d}"               # เปลี่ยนชื่อไฟล์ ต้นทางมีวงเล็บกับช่องว่างซึ่งจัดการยาก
        shutil.copy(img, RAW_DIR / f"{stem}.jpg")
        shutil.copy(lab, ANSWER_DIR / f"{stem}.txt")
        for line in lab.read_text().splitlines():
            if line.strip():
                counts[names[int(line.split()[0])]] += 1

    (RAW_DIR / "classes.txt").write_text(
        "\n".join(names[i] for i in sorted(names)) + "\n", encoding="utf-8"
    )
    (ANSWER_DIR / "README.txt").write_text(
        "เฉลยของรูปใน raw_images/ - อย่าเพิ่งเปิดดูจนกว่าจะ label เสร็จ\n"
        "รัน compare_labels.bat เพื่อเทียบผลงานกับเฉลย\n",
        encoding="utf-8",
    )

    # ข้อความ print ต้องเป็น ASCII - console ที่ไม่ใช่ codepage ไทยจะพังถ้าเจอภาษาไทย
    print(f"\nCopied {len(picked)} images to {RAW_DIR}")
    print(f"Answer key kept separately in {ANSWER_DIR} (do not peek yet)")
    print(f"Wrote classes.txt: {', '.join(names[i] for i in sorted(names))}")
    print("\nObjects in the answer key, by class:")
    for name, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {name:10s} {n:3d}")


if __name__ == "__main__":
    main()
