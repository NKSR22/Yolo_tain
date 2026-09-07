"""Lab 9 - ทดสอบสายสัญญาณระหว่าง Raspberry Pi กับ Arduino

ทดสอบได้ตั้งแต่ยังไม่ได้ต่อมอเตอร์หรือเซ็นเซอร์เลยแม้แต่ชิ้นเดียว
เพราะ firmware สั่งไฟบนบอร์ด (ขา 13) ให้สะท้อนสถานะมอเตอร์ไว้ด้วย
เห็นไฟกระพริบ = คำสั่งเดินทางจาก Pi ผ่าน USB ถึง Arduino ได้จริง

ใช้:
    python3 test_link.py

ข้อความ print ต้องเป็น ASCII - console ที่ไม่ใช่ codepage ไทยจะพังถ้าเจอภาษาไทย
"""
import sys
import time

from conveyor_link import ConveyorError, ConveyorLink


def step(n, total, text):
    print(f"[{n}/{total}] {text}")


def main():
    total = 6
    try:
        with ConveyorLink() as link:
            step(1, total, "Handshake")
            print(f"      PING -> {link.ping()}")
            print(f"      ID?  -> {link.identify()}")

            step(2, total, "Reading status before touching anything")
            print(f"      {link.status()}")

            step(3, total, "Motor ON for 2 seconds - watch the LED on the board")
            link.motor(True)
            print(f"      {link.status()}")
            time.sleep(2)

            step(4, total, "Motor OFF")
            link.motor(False)
            print(f"      {link.status()}")

            step(5, total, "Sorter pulse")
            link.sorter(True)
            time.sleep(0.5)
            link.sorter(False)
            print(f"      {link.status()}")

            step(6, total, "Sensor reading")
            present = link.sensor()
            print(f"      object present: {present}")
            if present:
                print("      NOTE: with nothing wired, the pin is held HIGH by the")
                print("      internal pull-up, so an active-low sensor reads as 'no")
                print("      object'. Seeing True here means something IS wired,")
                print("      or SENSOR_ACTIVE_LOW needs flipping in main.cpp.")

            print()
            print("=" * 58)
            print("  Link OK. Pi -> USB -> Arduino is working end to end.")
            print("=" * 58)
            return 0

    except ConveyorError as e:
        print()
        print("FAILED:", e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
