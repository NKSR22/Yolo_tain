"""Count objects per class as they cross a line on the conveyor.

Runs the same way on Windows and on the Raspberry Pi:

    python conveyor_count.py --model best.onnx --source 0
    python conveyor_count.py --model best.onnx --source clip.mp4 --no-show

Each detection is tied to a track (the same object from frame to frame) by
nearest centre. A track is counted once, the moment its centre crosses the
counting line, in whichever direction the belt is running. The belt direction
switch therefore needs no setting here; the direction is logged with each count.

All text printed or drawn is ASCII: OpenCV cannot draw Thai, and a Pi console
over SSH often shows Thai as '?'.
"""

import argparse
import csv
import math
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path


class Track:
    def __init__(self, track_id, center, class_name):
        self.id = track_id
        self.center = center
        self.missing = 0
        self.votes = Counter([class_name])
        self.counted = False

    @property
    def class_name(self):
        # Majority vote over the track's life: one misread frame at the line
        # does not change what the object is counted as.
        return self.votes.most_common(1)[0][0]


class LineCounter:
    """Track detections between frames and count line crossings.

    `axis` is the direction the belt moves in the image: "x" for a belt that runs
    left/right (the counting line is then vertical), "y" for up/down.
    `position` is where the line sits, as a fraction (0..1) of the frame.
    """

    def __init__(self, axis="x", position=0.5, max_jump=0.15, max_missing=10):
        if axis not in ("x", "y"):
            raise ValueError("axis must be 'x' or 'y'")
        self.axis = axis
        self.position = position
        self.max_jump = max_jump
        self.max_missing = max_missing
        self.tracks = {}
        self.next_id = 1
        self.counts = Counter()

    def line_coordinate(self, width, height):
        return self.position * (width if self.axis == "x" else height)

    def update(self, detections, width, height):
        """detections: list of (x1, y1, x2, y2, class_name).

        Returns the crossings in this frame as (track, direction) pairs, where
        direction is "+" (towards larger x/y) or "-".
        """
        max_distance = self.max_jump * max(width, height)
        line = self.line_coordinate(width, height)
        centers = [((x1 + x2) / 2, (y1 + y2) / 2, name) for x1, y1, x2, y2, name in detections]

        # Greedy nearest-centre matching: closest pairs first. Good enough for
        # a belt, where objects move a short, steady distance between frames.
        pairs = sorted(
            (math.dist(track.center, (cx, cy)), track_id, index)
            for track_id, track in self.tracks.items()
            for index, (cx, cy, _name) in enumerate(centers)
        )
        matched_tracks, matched_detections = set(), set()
        crossings = []
        for distance, track_id, index in pairs:
            if distance > max_distance:
                break
            if track_id in matched_tracks or index in matched_detections:
                continue
            matched_tracks.add(track_id)
            matched_detections.add(index)
            track = self.tracks[track_id]
            cx, cy, name = centers[index]
            before = self._side(track.center, line)
            track.center = (cx, cy)
            track.missing = 0
            track.votes[name] += 1
            after = self._side(track.center, line)
            if not track.counted and before != after:
                track.counted = True
                self.counts[track.class_name] += 1
                crossings.append((track, "+" if after > before else "-"))

        # Tracks not seen this frame may just be a missed detection; keep them
        # for a few frames before giving up on them.
        for track_id in list(self.tracks):
            if track_id not in matched_tracks:
                self.tracks[track_id].missing += 1
                if self.tracks[track_id].missing > self.max_missing:
                    del self.tracks[track_id]
        for index, (cx, cy, name) in enumerate(centers):
            if index not in matched_detections:
                self.tracks[self.next_id] = Track(self.next_id, (cx, cy), name)
                self.next_id += 1
        return crossings

    def _side(self, center, line):
        value = center[0] if self.axis == "x" else center[1]
        return 1 if value >= line else 0


def parse_args():
    parser = argparse.ArgumentParser(description="Count objects per class crossing a line.")
    parser.add_argument("--model", required=True, help="best.onnx or best.pt")
    parser.add_argument("--source", default="0", help="camera index (0) or a video file")
    parser.add_argument("--axis", choices=("x", "y"), default="x",
                        help="direction the belt moves in the image (default x: left/right)")
    parser.add_argument("--line", type=float, default=0.5,
                        help="counting line position as a fraction of the frame (default 0.5)")
    parser.add_argument("--conf", type=float, default=0.4, help="minimum confidence (default 0.4)")
    parser.add_argument("--no-show", action="store_true", help="no window (for SSH)")
    parser.add_argument("--log", default=None, help="CSV file for count events")
    return parser.parse_args()


def draw(frame, detections, counter, fps):
    import cv2

    height, width = frame.shape[:2]
    line = int(counter.line_coordinate(width, height))
    if counter.axis == "x":
        cv2.line(frame, (line, 0), (line, height), (0, 255, 255), 2)
    else:
        cv2.line(frame, (0, line), (width, line), (0, 255, 255), 2)
    for x1, y1, x2, y2, name in detections:
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 200, 0), 2)
        cv2.putText(frame, name, (int(x1), max(15, int(y1) - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)
    lines = [f"FPS {fps:.1f}"] + [f"{name}: {count}" for name, count in sorted(counter.counts.items())]
    for row, text in enumerate(lines):
        y = 28 + row * 28
        cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
        cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)


def main():
    args = parse_args()
    if not 0 < args.line < 1:
        print("[ERROR] --line must be between 0 and 1")
        return 1
    model_path = Path(args.model)
    if not model_path.is_file():
        print(f"[ERROR] Model not found: {model_path}")
        return 1

    import cv2
    from ultralytics import YOLO

    source = int(args.source) if args.source.isdigit() else args.source
    if isinstance(source, str) and not Path(source).is_file():
        print(f"[ERROR] Video not found: {source}")
        return 1
    model = YOLO(str(model_path), task="detect")
    # ONNX always on CPU: that is what the Pi has, and on a Windows PC with CUDA
    # installed, ultralytics 8.4 + onnxruntime 1.29 crash binding the input to
    # the GPU ("no data transfer registered for copying tensors").
    device = "cpu" if model_path.suffix.lower() == ".onnx" else None
    names = model.names
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Could not open source {args.source}")
        return 1

    log_path = Path(args.log or datetime.now().strftime("counts_%Y%m%d_%H%M%S.csv"))
    log_file = log_path.open("w", newline="", encoding="utf-8")
    log = csv.writer(log_file)
    log.writerow(["time", "track_id", "class", "direction"])

    counter = LineCounter(axis=args.axis, position=args.line)
    print(f"Model {model_path.name}, classes {list(names.values())}")
    print(f"Counting on a {'vertical' if args.axis == 'x' else 'horizontal'} line "
          f"at {args.line:.2f}. Press q in the window (or Ctrl+C) to stop.")
    fps, last = 0.0, time.perf_counter()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            result = model.predict(frame, conf=args.conf, device=device, verbose=False)[0]
            detections = [
                (*box, names[int(cls)])
                for box, cls in zip(result.boxes.xyxy.tolist(), result.boxes.cls.tolist())
            ]
            height, width = frame.shape[:2]
            for track, direction in counter.update(detections, width, height):
                stamp = datetime.now().strftime("%H:%M:%S")
                log.writerow([stamp, track.id, track.class_name, direction])
                log_file.flush()
                total = counter.counts[track.class_name]
                print(f"{stamp}  #{track.id:<4} {track.class_name:<16} {direction}  "
                      f"(total {track.class_name}: {total})")

            now = time.perf_counter()
            fps = 0.9 * fps + 0.1 / max(now - last, 1e-6) if fps else 1 / max(now - last, 1e-6)
            last = now
            if not args.no_show:
                draw(frame, detections, counter, fps)
                cv2.imshow("conveyor count", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        log_file.close()
        if not args.no_show:
            cv2.destroyAllWindows()

    print()
    print("=========== summary ===========")
    # A conveyor model has a handful of classes; list them all, zeros included.
    # A big model (80 COCO classes) would bury the counts, so list only hits.
    shown = names.values() if len(names) <= 20 else sorted(counter.counts)
    for name in shown:
        print(f"  {name:<20} {counter.counts.get(name, 0):>5}")
    print(f"  {'total':<20} {sum(counter.counts.values()):>5}")
    print(f"  average FPS          {fps:>7.1f}")
    print(f"Log: {log_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
