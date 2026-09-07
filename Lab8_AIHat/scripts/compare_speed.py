"""Lab 8 - เทียบความเร็ว CPU (Lab 7) กับ AI HAT (Lab 8)

ใส่ตัวเลขทางบรรทัดคำสั่ง:
    python3 compare_speed.py --cpu 150.2 --hailo 3.18
หรือรันเปล่า ๆ แล้วพิมพ์ตอบทีละค่า:
    python3 compare_speed.py

ข้อความ print ต้องเป็น ASCII - console ที่ไม่ใช่ codepage ไทยจะพังถ้าเจอภาษาไทย
"""
import argparse


def ask(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print("  Please enter a number greater than 0")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu", type=float,
                    help="average CPU inference time in ms, from Lab 7 fps_test.py")
    ap.add_argument("--hailo", type=float,
                    help="chip latency in ms, from Lab 8 run_detect_hailo.sh")
    args = ap.parse_args()

    cpu_ms = args.cpu if args.cpu else ask("CPU inference avg from Lab 7 (ms): ")
    hailo_ms = args.hailo if args.hailo else ask("AI HAT latency (ms): ")

    speedup = cpu_ms / hailo_ms
    print()
    print("=" * 58)
    print(f"  Raspberry Pi 5 CPU : {cpu_ms:7.2f} ms  ({1000 / cpu_ms:6.1f} FPS)")
    print(f"  Hailo AI HAT       : {hailo_ms:7.2f} ms  ({1000 / hailo_ms:6.1f} FPS)")
    print(f"  speedup            : {speedup:7.1f} x")
    print("=" * 58)
    print()
    print("How to read this:")
    print("  - Both numbers are chip time only. The CPU still has work to do either")
    print("    way (reading frames, resizing, drawing boxes), so the whole system")
    print("    does not get this much faster.")
    print("  - If the two sides run different models (CPU on YOLO11n, HAT on")
    print("    YOLOv6n), say so in your report - otherwise it is an unfair compare.")


if __name__ == "__main__":
    main()
