"""Windows GUI for capturing images of objects passing on a conveyor belt.

The belt runs on its own (a manual switch sets its direction); this program only
watches the camera. It saves a full frame each time an object reaches the middle
of the capture area, so every object is photographed once as it passes.
"""

import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
from PIL import Image, ImageTk


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = HERE.parent / "captured_images"
PREVIEW_WIDTH = 960
PREVIEW_HEIGHT = 540
WARMUP_FRAMES = 45
# Class names become YOLO class names, the YOLO-World prompt in Lab 10, and the
# label drawn by OpenCV on the Pi in Lab 12. OpenCV cannot draw Thai, and the
# prompt has to be English, so keep them to plain ASCII.
CLASS_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$")


class CaptureGate:
    """Fire once when an object arrives, then wait until it has moved on."""

    def __init__(self, enter_frames=2, clear_frames=8):
        self.enter_frames = enter_frames
        self.clear_frames = clear_frames
        self.armed = True
        self.present_frames = 0
        self.empty_frames = 0

    def update(self, present):
        if self.armed:
            self.present_frames = self.present_frames + 1 if present else 0
            if self.present_frames >= self.enter_frames:
                self.armed = False
                self.empty_frames = 0
                return True
        elif present:
            self.empty_frames = 0
        else:
            self.empty_frames += 1
            if self.empty_frames >= self.clear_frames:
                self.armed = True
                self.present_frames = 0
        return False


class MotionTrigger:
    """Decide, frame by frame, whether an object sits in the middle of the area.

    Background subtraction learns what the empty area looks like. Whatever
    differs from it is foreground. A frame counts as "object present" only when
    enough of the area is foreground AND the foreground's centre of mass lies in
    the middle half of the area, so the photo is taken with the object fully in
    view instead of the moment its edge crosses in. Which side it enters from
    does not matter, so reversing the belt needs no setting.
    """

    def __init__(self, threshold=0.02, center_band=0.25):
        self.threshold = threshold
        self.center_band = center_band
        self.subtractor = cv2.createBackgroundSubtractorMOG2(
            history=200, varThreshold=32, detectShadows=False
        )
        self.warmup_frames = 0
        self.gate = CaptureGate()
        self.foreground_ratio = 0.0
        self.centered = False

    @property
    def learning(self):
        return self.warmup_frames <= WARMUP_FRAMES

    def update(self, crop):
        """Feed one BGR crop of the capture area; return True to save this frame."""
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        learning_rate = 0.05 if self.warmup_frames < WARMUP_FRAMES else 0.002
        mask = self.subtractor.apply(gray, learningRate=learning_rate)
        self.warmup_frames += 1
        if self.learning:
            return False

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, None, iterations=1)
        height, width = mask.shape
        self.foreground_ratio = cv2.countNonZero(mask) / float(width * height)
        self.centered = False
        if self.foreground_ratio >= self.threshold:
            moments = cv2.moments(mask, binaryImage=True)
            cx = moments["m10"] / moments["m00"]
            cy = moments["m01"] / moments["m00"]
            self.centered = (
                abs(cx - width / 2) <= width * self.center_band
                and abs(cy - height / 2) <= height * self.center_band
            )
        return self.gate.update(self.centered)


def save_jpeg(path, frame):
    # cv2.imwrite silently fails on Windows when the path has non-ASCII
    # characters (a Thai user name or folder). Encode in memory, write with Python.
    ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        raise OSError("OpenCV could not encode the image.")
    path.write_bytes(buffer.tobytes())


class CaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conveyor Image Capture")
        self.root.geometry("1020x790")
        self.root.minsize(1000, 740)

        self.cap = None
        self.frame = None
        self.photo = None
        self.roi = None
        self.selecting_roi = False
        self.drag_start = None
        self.rectangle_item = None
        self.capture_active = False
        self.trigger = None
        self.saved_per_class = {}

        self.camera_var = tk.StringVar(value="0")
        self.class_var = tk.StringVar(value="")
        self.threshold_var = tk.StringVar(value="2.0")
        self.output_var = tk.StringVar(value=str(DEFAULT_OUTPUT_DIR))
        self.status_var = tk.StringVar(value="Open the camera to begin.")
        self.count_var = tk.StringVar(value="Saved: none yet")

        self._build_ui()
        self.root.bind("<space>", self._space_pressed)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(30, self.update_preview)

    def _build_ui(self):
        controls = ttk.Frame(self.root, padding=8)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Camera index").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(controls, from_=0, to=10, width=5, textvariable=self.camera_var).grid(
            row=0, column=1, padx=(4, 8), sticky="w"
        )
        ttk.Button(controls, text="Open camera", command=self.open_camera).grid(
            row=0, column=2, padx=4
        )
        ttk.Button(controls, text="Close camera", command=self.close_camera).grid(
            row=0, column=3, padx=4
        )
        ttk.Button(controls, text="Draw capture area", command=self.begin_roi_selection).grid(
            row=0, column=4, padx=(16, 4)
        )
        ttk.Label(controls, text="Motion threshold %").grid(
            row=0, column=5, padx=(16, 0), sticky="w"
        )
        ttk.Spinbox(
            controls, from_=0.5, to=20, increment=0.5, width=5,
            textvariable=self.threshold_var,
        ).grid(row=0, column=6, padx=4, sticky="w")

        ttk.Label(controls, text="Class name").grid(row=1, column=0, pady=(8, 0), sticky="w")
        ttk.Entry(controls, width=18, textvariable=self.class_var).grid(
            row=1, column=1, columnspan=2, padx=4, pady=(8, 0), sticky="w"
        )
        ttk.Button(controls, text="Start auto capture", command=self.start_capture).grid(
            row=1, column=3, padx=4, pady=(8, 0)
        )
        ttk.Button(controls, text="Stop auto capture", command=self.stop_capture).grid(
            row=1, column=4, padx=(16, 4), pady=(8, 0)
        )
        ttk.Button(controls, text="Capture now (Space)", command=self.capture_now).grid(
            row=1, column=5, columnspan=2, padx=(16, 4), pady=(8, 0), sticky="w"
        )

        ttk.Label(controls, text="Save under").grid(row=2, column=0, pady=(8, 0), sticky="w")
        ttk.Entry(controls, textvariable=self.output_var).grid(
            row=2, column=1, columnspan=6, padx=4, pady=(8, 0), sticky="ew"
        )
        ttk.Button(controls, text="Browse", command=self.choose_output_dir).grid(
            row=2, column=7, padx=4, pady=(8, 0), sticky="e"
        )
        controls.columnconfigure(6, weight=1)

        self.preview = tk.Canvas(
            self.root,
            width=PREVIEW_WIDTH,
            height=PREVIEW_HEIGHT,
            background="#202020",
            highlightthickness=0,
        )
        self.preview.pack(padx=8, pady=4)
        self.image_item = self.preview.create_image(0, 0, anchor=tk.NW)
        self.preview.bind("<ButtonPress-1>", self.roi_press)
        self.preview.bind("<B1-Motion>", self.roi_drag)
        self.preview.bind("<ButtonRelease-1>", self.roi_release)

        ttk.Label(self.root, textvariable=self.status_var, padding=(10, 2)).pack(
            fill=tk.X, anchor="w"
        )
        ttk.Label(self.root, textvariable=self.count_var, padding=(10, 2)).pack(
            fill=tk.X, anchor="w"
        )

    def open_camera(self):
        try:
            camera_index = int(self.camera_var.get())
        except ValueError:
            messagebox.showerror("Camera", "Camera index must be a whole number.")
            return

        self.close_camera()
        # The default backend (Media Foundation) gave 27.6 fps on a 640x480 USB
        # webcam; DirectShow gave 7 fps on the same camera. On a running belt,
        # 7 fps can skip an object entirely. DirectShow is only the fallback.
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            messagebox.showerror("Camera", f"Could not open camera index {camera_index}.")
            return

        self.cap = cap
        self.frame = None
        self.roi = None
        self.status_var.set(
            f"Camera {camera_index} is open. Click Draw capture area, "
            "then drag a box across the belt."
        )

    def close_camera(self):
        self.stop_capture()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.frame = None
        self.preview.itemconfigure(self.image_item, image="")
        if self.rectangle_item is not None:
            self.preview.delete(self.rectangle_item)
            self.rectangle_item = None

    def begin_roi_selection(self):
        if self.cap is None:
            messagebox.showinfo("Capture area", "Open the camera before drawing a capture area.")
            return
        self.stop_capture()
        self.selecting_roi = True
        self.status_var.set("Drag a box across the belt where objects pass.")

    def roi_press(self, event):
        # Clicking the picture moves keyboard focus off the text boxes, so the
        # Space key works as "Capture now" again.
        self.preview.focus_set()
        if not self.selecting_roi:
            return
        self.drag_start = (self._clamp_x(event.x), self._clamp_y(event.y))
        if self.rectangle_item is not None:
            self.preview.delete(self.rectangle_item)
        self.rectangle_item = self.preview.create_rectangle(
            event.x, event.y, event.x, event.y, outline="#00ff00", width=2
        )

    def roi_drag(self, event):
        if self.selecting_roi and self.drag_start and self.rectangle_item is not None:
            self.preview.coords(
                self.rectangle_item,
                self.drag_start[0],
                self.drag_start[1],
                self._clamp_x(event.x),
                self._clamp_y(event.y),
            )

    def roi_release(self, event):
        if not self.selecting_roi or self.drag_start is None or self.frame is None:
            return
        x1 = min(self.drag_start[0], self._clamp_x(event.x))
        y1 = min(self.drag_start[1], self._clamp_y(event.y))
        x2 = max(self.drag_start[0], self._clamp_x(event.x))
        y2 = max(self.drag_start[1], self._clamp_y(event.y))
        self.selecting_roi = False
        self.drag_start = None

        frame_height, frame_width = self.frame.shape[:2]
        left = int(x1 * frame_width / PREVIEW_WIDTH)
        top = int(y1 * frame_height / PREVIEW_HEIGHT)
        right = int(x2 * frame_width / PREVIEW_WIDTH)
        bottom = int(y2 * frame_height / PREVIEW_HEIGHT)
        if right - left < 16 or bottom - top < 16:
            self.status_var.set("Capture area is too small; draw a larger box.")
            return

        self.roi = (left, top, right, bottom)
        self.status_var.set("Capture area set. Type a class name, then Start auto capture.")

    @staticmethod
    def _clamp_x(x):
        return max(0, min(PREVIEW_WIDTH, x))

    @staticmethod
    def _clamp_y(y):
        return max(0, min(PREVIEW_HEIGHT, y))

    def _checked_class(self):
        label = self.class_var.get().strip()
        if not CLASS_NAME_PATTERN.match(label):
            messagebox.showerror(
                "Class name",
                "Use English letters, digits, _ or - only (for example red_cap).\n"
                "This name becomes the YOLO class name in Lab 10.",
            )
            return None
        return label

    def start_capture(self):
        if self.cap is None:
            messagebox.showerror("Auto capture", "Open the camera first.")
            return
        if self.roi is None:
            messagebox.showerror("Auto capture", "Draw a capture area first.")
            return
        if self._checked_class() is None:
            return
        try:
            threshold = float(self.threshold_var.get()) / 100
        except ValueError:
            threshold = 0
        if not 0 < threshold < 1:
            messagebox.showerror("Auto capture", "Motion threshold must be between 0 and 100.")
            return

        self.trigger = MotionTrigger(threshold=threshold)
        self.capture_active = True

    def stop_capture(self):
        if self.capture_active:
            self.status_var.set("Auto capture stopped.")
        self.capture_active = False
        self.trigger = None

    def _space_pressed(self, event):
        # Typing a space in a text box must not take a photo.
        if isinstance(event.widget, (tk.Entry, ttk.Entry, ttk.Spinbox)):
            return
        self.capture_now()

    def capture_now(self):
        if self.frame is None:
            return
        label = self._checked_class()
        if label is not None:
            self._save_image(self.frame, label)

    def choose_output_dir(self):
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)

    def _process_capture_area(self, frame):
        left, top, right, bottom = self.roi
        fire = self.trigger.update(frame[top:bottom, left:right])
        if self.trigger.learning:
            self.status_var.set(
                f"Learning the belt: {self.trigger.warmup_frames}/{WARMUP_FRAMES} frames. "
                "Keep objects out of the box (the belt may keep running)."
            )
            return
        if fire:
            self._save_image(frame, self.class_var.get().strip())
            return
        state = "object in the middle" if self.trigger.centered else (
            "waiting for an object" if self.trigger.gate.armed else "waiting for it to leave"
        )
        self.status_var.set(
            f"Auto capture: motion {self.trigger.foreground_ratio * 100:.1f}% "
            f"(threshold {self.trigger.threshold * 100:.1f}%), {state}."
        )

    def _save_image(self, frame, label):
        output_text = self.output_var.get().strip()
        if not output_text:
            self.stop_capture()
            messagebox.showerror("Save image", "Choose a folder to save images in.")
            return
        folder = Path(output_text).expanduser() / label
        path = folder / (datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".jpg")
        try:
            folder.mkdir(parents=True, exist_ok=True)
            save_jpeg(path, frame)
        except OSError as exc:
            self.stop_capture()
            messagebox.showerror("Save image", f"Could not save {path}:\n{exc}")
            return
        self.saved_per_class[label] = self.saved_per_class.get(label, 0) + 1
        self.status_var.set(f"Saved {path.name} to {folder}")
        self.count_var.set(
            "Saved this session: "
            + ", ".join(f"{name} {count}" for name, count in sorted(self.saved_per_class.items()))
        )

    def update_preview(self):
        if self.cap is not None:
            ok, frame = self.cap.read()
            if ok and frame is not None:
                self.frame = frame
                if self.capture_active and self.roi is not None:
                    self._process_capture_area(frame)
                self._draw_preview(frame)
            else:
                self.stop_capture()
                self.status_var.set("Camera frame read failed; auto capture stopped.")
        self.root.after(30, self.update_preview)

    def _draw_preview(self, frame):
        resized = cv2.resize(frame, (PREVIEW_WIDTH, PREVIEW_HEIGHT))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.preview.itemconfigure(self.image_item, image=self.photo)

        if self.roi is not None and not self.selecting_roi:
            frame_height, frame_width = frame.shape[:2]
            left, top, right, bottom = self.roi
            coords = (
                left * PREVIEW_WIDTH / frame_width,
                top * PREVIEW_HEIGHT / frame_height,
                right * PREVIEW_WIDTH / frame_width,
                bottom * PREVIEW_HEIGHT / frame_height,
            )
            # Green while idle, yellow while learning or waiting, red when an
            # object sits in the middle of the box.
            color = "#00ff00"
            if self.trigger is not None:
                color = "#ff4040" if self.trigger.centered else "#ffd000"
            if self.rectangle_item is None:
                self.rectangle_item = self.preview.create_rectangle(
                    *coords, outline=color, width=2
                )
            else:
                self.preview.coords(self.rectangle_item, *coords)
                self.preview.itemconfigure(self.rectangle_item, outline=color)

    def close(self):
        self.close_camera()
        self.root.destroy()


def main():
    root = tk.Tk()
    CaptureApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
