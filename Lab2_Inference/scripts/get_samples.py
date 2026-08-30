"""Lab 2 - เตรียมไฟล์ตัวอย่างสำหรับทดลอง Detection

สร้างไฟล์ในโฟลเดอร์ Lab2_Inference/samples/
  test.jpg  - ภาพตัวอย่าง (ดาวน์โหลดจาก Ultralytics)
  test2.jpg - ภาพตัวอย่างที่สอง
  test.mp4  - วิดีโอสั้น ๆ สร้างจากภาพตัวอย่าง (ไว้ทดสอบ predict_video.bat)
"""
import urllib.request
from pathlib import Path

import cv2

SAMPLES = Path(__file__).resolve().parent.parent / "samples"
IMAGES = {
    "test.jpg": "https://ultralytics.com/images/bus.jpg",
    "test2.jpg": "https://ultralytics.com/images/zidane.jpg",
}
VIDEO_SECONDS = 5
FPS = 20


def download_images():
    SAMPLES.mkdir(exist_ok=True)
    for name, url in IMAGES.items():
        dest = SAMPLES / name
        if dest.exists():
            print(f"[skip] {name} already exists")
            continue
        print(f"[get ] {name} <- {url}")
        urllib.request.urlretrieve(url, dest)


def make_video():
    """สร้างวิดีโอโดยเลื่อนกรอบ (pan) ไปบนภาพตัวอย่าง เพื่อให้มีไฟล์ .mp4 ไว้ทดสอบ"""
    dest = SAMPLES / "test.mp4"
    if dest.exists():
        print("[skip] test.mp4 already exists")
        return
    img = cv2.imread(str(SAMPLES / "test.jpg"))
    if img is None:
        print("[warn] test.jpg not found, skipping video creation")
        return

    h, w = img.shape[:2]
    crop_w, crop_h = int(w * 0.8), int(h * 0.8)
    n_frames = VIDEO_SECONDS * FPS
    writer = cv2.VideoWriter(str(dest), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (crop_w, crop_h))
    for i in range(n_frames):
        # เลื่อนไป-กลับ เพื่อให้เห็นการเคลื่อนไหวในวิดีโอ
        t = i / (n_frames - 1)
        t = 2 * t if t < 0.5 else 2 * (1 - t)
        x = int(t * (w - crop_w))
        y = int(t * (h - crop_h))
        writer.write(img[y:y + crop_h, x:x + crop_w])
    writer.release()
    print(f"[make] test.mp4 ({VIDEO_SECONDS}s, {crop_w}x{crop_h})")


if __name__ == "__main__":
    try:
        download_images()
    except Exception as e:  # noqa: BLE001 - แจ้งผู้ใช้สั้น ๆ แทน traceback ยาว
        print(f"[error] download failed ({e})")
        print(r"        Check your internet, or copy your own image to Lab2_Inference\samples\test.jpg")
    make_video()
    print(f"\nSample files are in: {SAMPLES}")
