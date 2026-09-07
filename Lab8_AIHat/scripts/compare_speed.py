"""Lab 8 - เทียบความเร็ว CPU (Lab 7) กับ AI HAT (Lab 8)

ใส่ตัวเลขทางบรรทัดคำสั่ง:
    python3 compare_speed.py --cpu 150.2 --hailo 3.18
หรือรันเปล่า ๆ แล้วพิมพ์ตอบทีละค่า:
    python3 compare_speed.py
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
        print("  กรุณาใส่ตัวเลขมากกว่า 0")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu", type=float,
                    help="เวลา inference เฉลี่ยบน CPU (ms) จาก Lab 7 fps_test.py")
    ap.add_argument("--hailo", type=float,
                    help="latency ของชิป (ms) จาก Lab 8 run_detect_hailo.sh")
    args = ap.parse_args()

    cpu_ms = args.cpu if args.cpu else ask("CPU inference เฉลี่ยจาก Lab 7 (ms): ")
    hailo_ms = args.hailo if args.hailo else ask("latency ของ AI HAT (ms): ")

    speedup = cpu_ms / hailo_ms
    print()
    print("=" * 52)
    print(f"  Raspberry Pi 5 CPU : {cpu_ms:7.2f} ms  ({1000 / cpu_ms:6.1f} FPS)")
    print(f"  Hailo AI HAT       : {hailo_ms:7.2f} ms  ({1000 / hailo_ms:6.1f} FPS)")
    print(f"  เร็วขึ้น            : {speedup:7.1f} เท่า")
    print("=" * 52)
    print()
    print("อ่านผลให้เป็น:")
    print("  - ตัวเลขนี้เทียบ 'เวลาในชิป' ทั้งคู่ ยังไม่รวมงานที่ CPU ต้องทำอยู่ดี")
    print("    (อ่านภาพจากกล้อง ย่อขนาด วาดกรอบ) ระบบจริงจึงไม่ได้เร็วขึ้นเท่านี้ทั้งหมด")
    print("  - ถ้าโมเดลสองฝั่งคนละตัว (เช่น CPU รัน YOLO11n แต่ HAT รัน YOLOv6n)")
    print("    ให้ระบุไว้ในรายงานด้วย ไม่งั้นเป็นการเทียบที่ไม่ยุติธรรม")


if __name__ == "__main__":
    main()
