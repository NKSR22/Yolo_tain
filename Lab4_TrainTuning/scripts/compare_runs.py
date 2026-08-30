"""Lab 4 - เอาผลของทุกรอบการเทรนมาเรียงเทียบกันในตารางเดียว

อ่าน runs/detect/*/results.csv ที่ Ultralytics เขียนไว้ให้ทุกรอบ
แล้วดึงค่าของ epoch ที่ดีที่สุด (ยึด mAP50-95 เหมือนที่ YOLO ใช้เลือก best.pt)

    python compare_runs.py                 เทียบทุกรอบที่มี
    python compare_runs.py baseline full   เลือกเฉพาะบางรอบ
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RUNS = ROOT / "runs" / "detect"

COLUMNS = [
    ("mAP50-95", "metrics/mAP50-95(B)"),
    ("mAP50", "metrics/mAP50(B)"),
    ("precision", "metrics/precision(B)"),
    ("recall", "metrics/recall(B)"),
]


def read_run(run_dir):
    csv_path = run_dir / "results.csv"
    if not csv_path.exists():
        return None
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = [{k.strip(): v for k, v in row.items()} for row in csv.DictReader(f)]
    if not rows:
        return None

    key = COLUMNS[0][1]
    if key not in rows[0]:
        return None
    best = max(rows, key=lambda r: float(r.get(key) or 0))
    return {
        "epochs": len(rows),
        "best_epoch": int(float(best.get("epoch", 0))),
        "time_s": float(rows[-1].get("time") or 0),
        "values": {label: float(best.get(col) or 0) for label, col in COLUMNS},
    }


def count_images(run_dir):
    """อ่านจำนวนภาพ train จาก args.yaml -> data.yaml เพื่อให้เห็นว่ารอบนั้นเทรนด้วยข้อมูลเท่าไร"""
    args_file = run_dir / "args.yaml"
    if not args_file.exists():
        return ""
    data = ""
    for line in args_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("data:"):
            data = line.split(":", 1)[1].strip()
            break
    if not data:
        return ""
    try:
        from ultralytics.data.utils import check_det_dataset

        info = check_det_dataset(data)
        train = Path(info["train"])
        n = len(list(train.glob("*.jpg"))) + len(list(train.glob("*.png")))
        return f"{n}"
    except Exception:  # noqa: BLE001 - ถ้าหา dataset ไม่เจอก็แค่เว้นช่องว่างไว้
        return ""


def main():
    wanted = sys.argv[1:]
    if not RUNS.exists():
        raise SystemExit(f"No runs found at {RUNS}. Train something first.")

    dirs = sorted(d for d in RUNS.iterdir() if d.is_dir() and (d / "results.csv").exists())
    if wanted:
        dirs = [d for d in dirs if d.name in wanted]
    if not dirs:
        raise SystemExit("No training runs with results.csv found.")

    rows = []
    for d in dirs:
        info = read_run(d)
        if info:
            rows.append((d.name, info, count_images(d)))
    if not rows:
        raise SystemExit("Found run folders but none had usable results.csv (predict runs have none).")

    name_w = max(len(n) for n, _, _ in rows) + 2
    header = f"{'run':<{name_w}}{'imgs':>6}{'epochs':>8}{'best@':>7}" + "".join(
        f"{label:>11}" for label, _ in COLUMNS) + f"{'time':>9}"
    print(header)
    print("-" * len(header))
    for name, info, imgs in rows:
        line = f"{name:<{name_w}}{imgs:>6}{info['epochs']:>8}{info['best_epoch']:>7}"
        line += "".join(f"{info['values'][label]:>11.3f}" for label, _ in COLUMNS)
        line += f"{info['time_s'] / 60:>8.1f}m"
        print(line)

    print("\nAll numbers are from the best epoch of each run, ranked by mAP50-95")
    print("(the same measure YOLO uses when it decides which weights to keep as best.pt).")


if __name__ == "__main__":
    main()
