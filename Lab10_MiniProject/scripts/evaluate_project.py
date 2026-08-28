import csv
from collections import Counter
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "logs" / "session.csv"

def main():
    if not LOG_PATH.exists():
        print("No log file found. Run main.py first.")
        return
    counts = Counter()
    with open(LOG_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            counts[row["class"]] += 1
    print("Detections summary:")
    for cls, n in counts.most_common():
        print(f"  {cls}: {n}")

if __name__ == "__main__":
    main()
