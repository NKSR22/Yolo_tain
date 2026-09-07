/*
 * Lab 9 - Firmware ฝั่ง Arduino Uno สำหรับชุดสายพานคัดแยก
 *
 * ทำไมงานนี้ถึงอยู่บน Arduino ไม่ใช่บน Raspberry Pi โดยตรง:
 * บอร์ด AI HAT ของ Lab 8 เสียบทับหัว GPIO ของ Pi ไปแล้ว ไม่เหลือขาว่างให้ต่อ
 * มอเตอร์/เซ็นเซอร์ เลยแบ่งหน้าที่กันใหม่เป็น
 *     Pi     = กล้อง + YOLO + ตัดสินใจ
 *     Arduino = ขับมอเตอร์ + อ่านเซ็นเซอร์ (งานที่ต้องการจังหวะเวลาแน่นอน)
 * คุยกันผ่านสาย USB เส้นเดียวด้วยข้อความบรรทัดต่อบรรทัด
 *
 * โปรโตคอลตั้งใจให้เป็นข้อความอ่านออก ไม่ใช่ไบต์ดิบ เพราะนักศึกษาต้องเปิด
 * Serial Monitor พิมพ์คำสั่งทดสอบเองได้ โดยไม่ต้องรันฝั่ง Python เลย
 *
 * คำสั่งที่รับ (พิมพ์แล้วกด Enter)
 *   PING     -> PONG
 *   ID?      -> ID conveyor-uno v1
 *   M1 / M0  -> เดินสายพาน / หยุดสายพาน
 *   S1 / S0  -> ดันตัวคัดแยกออก / ดึงกลับ
 *   SENSOR?  -> SENSOR 0 หรือ SENSOR 1
 *   STATUS?  -> STATUS motor=0 sorter=0 sensor=0
 *
 * ทุกคำสั่งตอบ OK <คำสั่ง> หรือ ERR <เหตุผล> เสมอ
 * ฝั่ง Pi จะได้รอคำตอบที่แน่นอน ไม่ต้องเดาด้วยการ sleep
 *
 * เหตุการณ์ที่ส่งเองโดยไม่ต้องถาม
 *   EVENT OBJECT   เมื่อเซ็นเซอร์เปลี่ยนจากว่างเป็นเจอวัตถุ
 *
 * ข้อความทุกบรรทัดเป็น ASCII ตามธรรมเนียมของรีโปนี้
 */

#include <Arduino.h>

// ---- ขาที่ใช้ ----
// ยังไม่ได้ต่ออุปกรณ์จริงตอนเขียนไฟล์นี้ เลขขาชุดนี้จึงเป็นค่าตั้งต้นที่เลือกไว้
// ให้ต่อง่าย ถ้าวงจรของกลุ่มใช้ขาอื่นให้แก้ตรงนี้ที่เดียว
const uint8_t PIN_MOTOR_IN1 = 4;   // ทิศทางมอเตอร์ ขา 1 (L298N IN1)
const uint8_t PIN_MOTOR_IN2 = 5;   // ทิศทางมอเตอร์ ขา 2 (L298N IN2)
const uint8_t PIN_MOTOR_PWM = 9;   // ความเร็วมอเตอร์ - ต้องเป็นขา PWM (L298N ENA)
const uint8_t PIN_SENSOR    = 2;   // เซ็นเซอร์ IR - ขา 2 รองรับ interrupt
const uint8_t PIN_SORTER    = 8;   // รีเลย์/โซลินอยด์ของตัวคัดแยก

// ไฟบนบอร์ด (ขา 13) สะท้อนสถานะมอเตอร์
// จุดนี้ตั้งใจใส่ไว้ เพื่อให้ทดสอบทั้งเส้นทางได้ตั้งแต่ Pi -> USB -> Arduino
// โดยยังไม่ต้องต่ออุปกรณ์อะไรเลยสักชิ้น เห็นไฟกระพริบ = คำสั่งถึงจริง
const uint8_t PIN_LED = LED_BUILTIN;

const unsigned long BAUD = 115200;
const uint8_t MOTOR_SPEED = 200;      // 0-255 ปรับตามแรงที่สายพานต้องการ
const unsigned long DEBOUNCE_MS = 30; // กันเซ็นเซอร์กระพริบตอนขอบสัญญาณ

// เซ็นเซอร์ IR ส่วนใหญ่เป็นแบบ active-low (เจอวัตถุ = ขาลงเป็น LOW)
// ถ้าของกลุ่มไหนกลับด้าน ให้เปลี่ยนเป็น false ค่าเดียว ไม่ต้องไปแก้ที่อื่น
const bool SENSOR_ACTIVE_LOW = true;

bool motorOn = false;
bool sorterOn = false;
bool lastObject = false;
unsigned long lastEdgeMs = 0;

String line;

bool objectPresent() {
    int raw = digitalRead(PIN_SENSOR);
    return SENSOR_ACTIVE_LOW ? (raw == LOW) : (raw == HIGH);
}

void setMotor(bool on) {
    motorOn = on;
    // เดินหน้าอย่างเดียว สายพานไม่ต้องถอยหลัง
    digitalWrite(PIN_MOTOR_IN1, on ? HIGH : LOW);
    digitalWrite(PIN_MOTOR_IN2, LOW);
    analogWrite(PIN_MOTOR_PWM, on ? MOTOR_SPEED : 0);
    digitalWrite(PIN_LED, on ? HIGH : LOW);
}

void setSorter(bool on) {
    sorterOn = on;
    digitalWrite(PIN_SORTER, on ? HIGH : LOW);
}

void sendStatus() {
    Serial.print(F("STATUS motor="));
    Serial.print(motorOn ? 1 : 0);
    Serial.print(F(" sorter="));
    Serial.print(sorterOn ? 1 : 0);
    Serial.print(F(" sensor="));
    Serial.println(objectPresent() ? 1 : 0);
}

void handle(const String &cmd) {
    if (cmd == F("PING")) {
        Serial.println(F("PONG"));
    } else if (cmd == F("ID?")) {
        Serial.println(F("ID conveyor-uno v1"));
    } else if (cmd == F("M1")) {
        setMotor(true);
        Serial.println(F("OK M1"));
    } else if (cmd == F("M0")) {
        setMotor(false);
        Serial.println(F("OK M0"));
    } else if (cmd == F("S1")) {
        setSorter(true);
        Serial.println(F("OK S1"));
    } else if (cmd == F("S0")) {
        setSorter(false);
        Serial.println(F("OK S0"));
    } else if (cmd == F("SENSOR?")) {
        Serial.print(F("SENSOR "));
        Serial.println(objectPresent() ? 1 : 0);
    } else if (cmd == F("STATUS?")) {
        sendStatus();
    } else if (cmd.length() > 0) {
        // ตอบกลับพร้อมคำสั่งที่ได้รับ เวลาดีบักจะได้รู้ว่ามันอ่านได้เป็นอะไร
        Serial.print(F("ERR unknown command: "));
        Serial.println(cmd);
    }
}

void setup() {
    pinMode(PIN_MOTOR_IN1, OUTPUT);
    pinMode(PIN_MOTOR_IN2, OUTPUT);
    pinMode(PIN_MOTOR_PWM, OUTPUT);
    pinMode(PIN_SORTER, OUTPUT);
    pinMode(PIN_LED, OUTPUT);
    // เปิด pull-up ในตัว เพื่อให้ขาเซ็นเซอร์ที่ยังไม่ได้ต่ออะไรมีค่าแน่นอน
    // ไม่ลอยไปมาจนอ่านได้มั่ว
    pinMode(PIN_SENSOR, INPUT_PULLUP);

    setMotor(false);
    setSorter(false);

    Serial.begin(BAUD);
    while (!Serial) {
        ;  // Uno ไม่ต้องรอจริง แต่ใส่ไว้ให้ย้ายไปบอร์ดที่ใช้ USB native ได้เลย
    }
    line.reserve(32);
    Serial.println(F("READY conveyor-uno v1"));
}

void loop() {
    while (Serial.available() > 0) {
        char c = (char)Serial.read();
        if (c == '\n') {
            line.trim();          // ตัด \r ที่ติดมาจาก Serial Monitor บน Windows
            handle(line);
            line = "";
        } else if (line.length() < 30) {
            line += c;
        }
        // ถ้ายาวเกิน 30 ตัวก็ทิ้งตัวที่เกิน กันบัฟเฟอร์ล้นบนบอร์ดที่มี RAM 2 KB
    }

    // แจ้งเหตุการณ์เฉพาะ "ตอนเปลี่ยนสถานะ" ไม่ใช่ส่งรัวทุกลูป
    bool now = objectPresent();
    if (now != lastObject && millis() - lastEdgeMs > DEBOUNCE_MS) {
        lastEdgeMs = millis();
        lastObject = now;
        if (now) {
            Serial.println(F("EVENT OBJECT"));
        }
    }
}
