"""Lab 9 - ดูค่าเซ็นเซอร์แบบสด ๆ ผ่าน Arduino

ใช้ตอนต่อเซ็นเซอร์เสร็จแล้ว เพื่อดูว่ามันตอบสนองจริงไหม และตอบกลับด้านถูกไหม
เอามือบังหน้าเซ็นเซอร์แล้วดูว่าเลขเปลี่ยนหรือเปล่า

ใช้:
    python3 test_sensor.py            # อ่านค่าทุก 0.2 วินาที
    python3 test_sensor.py --events   # รอเฉพาะตอนเซ็นเซอร์เจอวัตถุ

ถ้าค่าที่อ่านได้กลับด้านกับความจริง (ไม่มีของแต่ขึ้น 1) ให้แก้
SENSOR_ACTIVE_LOW ใน arduino/src/main.cpp แล้วอัปโหลดใหม่

ข้อความ print ต้องเป็น ASCII - console ที่ไม่ใช่ codepage ไทยจะพังถ้าเจอภาษาไทย
"""
import argparse
import sys
import time

from conveyor_link import ConveyorError, ConveyorLink


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", action="store_true",
                    help="wait for EVENT OBJECT lines instead of polling")
    ap.add_argument("--period", type=float, default=0.2, help="seconds between reads")
    args = ap.parse_args()

    try:
        with ConveyorLink() as link:
            print(link.identify())
            if args.events:
                print("Waiting for objects. Ctrl+C to stop.")
                n = 0
                while True:
                    if link.wait_for_object(timeout=1.0):
                        n += 1
                        print(f"  object #{n} at {time.strftime('%H:%M:%S')}")
            else:
                print("Reading the sensor. Ctrl+C to stop.")
                last = None
                while True:
                    value = link.sensor()
                    # พิมพ์เฉพาะตอนค่าเปลี่ยน ไม่งั้นจอเต็มไปด้วยบรรทัดซ้ำ
                    if value != last:
                        print(f"  sensor = {1 if value else 0}"
                              f"  ({'object' if value else 'clear'})")
                        last = value
                    time.sleep(args.period)

    except KeyboardInterrupt:
        print()
        print("Stopped.")
        return 0
    except ConveyorError as e:
        print("Link error:", e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
