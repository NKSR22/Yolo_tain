"""Lab 5 - รวบรวมไฟล์ผลการประเมินไว้ในที่เดียวเพื่อใส่รายงาน

หาโฟลเดอร์ผลของรอบล่าสุดเอง (ไม่ใช่ hardcode ชื่อ val) เพราะถ้ารัน evaluate ซ้ำ
Ultralytics จะสร้าง val2, val3 ... เพิ่มขึ้นเรื่อย ๆ

    python export_report.py            เอารอบล่าสุดที่ขึ้นต้นด้วย val
    python export_report.py val_test   ระบุชื่อรอบเอง
"""
import shutil
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
RUNS = LAB_DIR.parent / "runs" / "detect"
REPORT = LAB_DIR / "report"
WANTED = ["confusion_matrix.png", "confusion_matrix_normalized.png",
          "BoxPR_curve.png", "BoxF1_curve.png", "BoxP_curve.png", "BoxR_curve.png",
          "val_batch0_pred.jpg", "val_batch0_labels.jpg"]


def pick_run():
    if len(sys.argv) > 1:
        d = RUNS / sys.argv[1]
        if not d.exists():
            raise SystemExit(f"Not found: {d}")
        return d
    candidates = [d for d in RUNS.iterdir()
                  if d.is_dir() and d.name.startswith("val") and (d / "confusion_matrix.png").exists()]
    if not candidates:
        raise SystemExit(f"No evaluation runs found in {RUNS}. Run evaluate.bat first.")
    return max(candidates, key=lambda d: d.stat().st_mtime)


def main():
    run = pick_run()
    REPORT.mkdir(exist_ok=True)
    print(f"Collecting from {run}")

    copied = 0
    for name in WANTED:
        src = run / name
        if src.exists():
            shutil.copy(src, REPORT / name)
            print(f"  + {name}")
            copied += 1
        else:
            print(f"  - {name} (not produced by this run)")

    print(f"\n{copied} file(s) copied to {REPORT}")
    print("Put these straight into your report - the confusion matrix and the PR")
    print("curve are the two that examiners actually ask about.")


if __name__ == "__main__":
    main()
