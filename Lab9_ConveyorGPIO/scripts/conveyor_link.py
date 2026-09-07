"""Lab 9 - ตัวเชื่อมระหว่าง Raspberry Pi กับ Arduino Uno ผ่านสาย USB

ทุกฟังก์ชันที่ส่งคำสั่งจะ "รอคำตอบ" เสมอ ไม่ใช่ส่งแล้วนอน sleep เอา
เพราะการ sleep เดาเวลาคือที่มาของบั๊กที่หาสาเหตุยากที่สุดในงานคุมฮาร์ดแวร์
(บางครั้งทัน บางครั้งไม่ทัน แล้วแต่จังหวะ)

ใช้:
    from conveyor_link import ConveyorLink
    with ConveyorLink() as link:
        print(link.identify())
        link.motor(True)
        print(link.status())

ข้อความ print ต้องเป็น ASCII - console ที่ไม่ใช่ codepage ไทยจะพังถ้าเจอภาษาไทย
"""
import time

import serial   # มาจากแพ็กเกจ pyserial ไม่ใช่ serial

from config import SERIAL_PORT, SERIAL_BAUD, SERIAL_TIMEOUT, RESET_WAIT


class ConveyorError(RuntimeError):
    pass


class ConveyorLink:
    def __init__(self, port=SERIAL_PORT, baud=SERIAL_BAUD, timeout=SERIAL_TIMEOUT):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser = None

    # ---- เปิด/ปิดการเชื่อมต่อ ----

    def open(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
        except serial.SerialException as e:
            raise ConveyorError(
                f"Cannot open {self.port}: {e}\n"
                "  - is the Arduino plugged in?   ls -l /dev/ttyACM*\n"
                "  - are you in the dialout group? groups\n"
                "  - is PlatformIO monitor still open on the same port?"
            ) from e

        # เปิดพอร์ตแล้ว Uno จะรีเซ็ตตัวเองเสมอ (สาย DTR ไปดึงขา reset)
        # ต้องรอให้บูตจบก่อน ไม่งั้นคำสั่งแรกจะหายไปกับ bootloader
        time.sleep(RESET_WAIT)
        self.ser.reset_input_buffer()
        return self

    def close(self):
        if self.ser and self.ser.is_open:
            try:
                self.command("M0")      # อย่าปล่อยให้มอเตอร์ค้างหมุนตอนโปรแกรมจบ
                self.command("S0")
            except ConveyorError:
                pass
            self.ser.close()
        self.ser = None

    def __enter__(self):
        return self.open()

    def __exit__(self, *exc):
        self.close()
        return False

    # ---- ระดับล่าง ----

    def _readline(self):
        raw = self.ser.readline()
        if not raw:
            raise ConveyorError(
                f"No reply from the Arduino within {self.timeout}s.\n"
                "  - is the firmware uploaded? run ./upload_arduino.sh\n"
                "  - does monitor_speed match BAUD in main.cpp?"
            )
        return raw.decode("ascii", errors="replace").strip()

    def command(self, cmd, expect_prefix=None):
        """ส่งคำสั่งหนึ่งบรรทัดแล้วคืนคำตอบบรรทัดแรกที่ไม่ใช่ EVENT"""
        if self.ser is None:
            raise ConveyorError("Link is not open - call open() first")
        self.ser.reset_input_buffer()
        self.ser.write((cmd + "\n").encode("ascii"))
        self.ser.flush()

        # ข้ามบรรทัด EVENT ที่บอร์ดอาจส่งแทรกเข้ามาระหว่างรอคำตอบ
        for _ in range(10):
            reply = self._readline()
            if not reply.startswith("EVENT"):
                break
        else:
            raise ConveyorError(f"Only EVENT lines came back for '{cmd}'")

        if reply.startswith("ERR"):
            raise ConveyorError(f"Arduino rejected '{cmd}': {reply}")
        if expect_prefix and not reply.startswith(expect_prefix):
            raise ConveyorError(
                f"Unexpected reply to '{cmd}': got '{reply}', expected '{expect_prefix}...'"
            )
        return reply

    # ---- ระดับใช้งาน ----

    def ping(self):
        return self.command("PING", expect_prefix="PONG")

    def identify(self):
        return self.command("ID?", expect_prefix="ID ")

    def motor(self, on):
        return self.command("M1" if on else "M0", expect_prefix="OK")

    def sorter(self, on):
        return self.command("S1" if on else "S0", expect_prefix="OK")

    def sensor(self):
        """คืน True เมื่อเซ็นเซอร์เจอวัตถุ"""
        reply = self.command("SENSOR?", expect_prefix="SENSOR ")
        return reply.split()[1] == "1"

    def status(self):
        """คืน dict เช่น {'motor': 0, 'sorter': 0, 'sensor': 1}"""
        reply = self.command("STATUS?", expect_prefix="STATUS ")
        out = {}
        for part in reply.split()[1:]:
            key, _, value = part.partition("=")
            out[key] = int(value)
        return out

    def wait_for_object(self, timeout=None):
        """รอบรรทัด EVENT OBJECT คืน True ถ้าเจอ, False ถ้าหมดเวลา"""
        deadline = None if timeout is None else time.monotonic() + timeout
        while deadline is None or time.monotonic() < deadline:
            raw = self.ser.readline()
            if raw and raw.decode("ascii", errors="replace").strip() == "EVENT OBJECT":
                return True
        return False
