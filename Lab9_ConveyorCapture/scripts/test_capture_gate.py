import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from capture_gui import CLASS_NAME_PATTERN, WARMUP_FRAMES, CaptureGate, MotionTrigger, save_jpeg


def belt_frame(object_x=None, width=320, height=120, shift=0):
    """A grey belt with stripes that scroll by `shift`, plus an optional dark box."""
    frame = np.full((height, width, 3), 150, np.uint8)
    for x in range(-40, width + 40, 40):
        cv2.line(frame, (x + shift % 40, 0), (x + shift % 40, height), (140, 140, 140), 2)
    if object_x is not None:
        cv2.rectangle(frame, (object_x - 20, 35), (object_x + 20, 85), (30, 60, 200), -1)
    return frame


class CaptureGateTests(unittest.TestCase):
    def test_captures_once_until_the_area_is_clear(self):
        gate = CaptureGate(enter_frames=2, clear_frames=3)

        self.assertFalse(gate.update(True))
        self.assertTrue(gate.update(True))
        self.assertFalse(gate.update(True))
        self.assertFalse(gate.update(False))
        self.assertFalse(gate.update(False))
        self.assertFalse(gate.update(False))
        self.assertFalse(gate.update(True))
        self.assertTrue(gate.update(True))


class MotionTriggerTests(unittest.TestCase):
    def run_pass(self, positions):
        # The belt keeps running the whole time, so its stripes scroll every frame.
        trigger = MotionTrigger()
        tick = 0
        for tick in range(WARMUP_FRAMES + 5):
            self.assertFalse(trigger.update(belt_frame(shift=tick * 3)))
        fired_at = []
        for x in positions:
            tick += 1
            if trigger.update(belt_frame(x, shift=tick * 3)):
                fired_at.append(x)
        return fired_at

    def test_one_photo_per_object_with_the_object_near_the_middle(self):
        left_to_right = self.run_pass(range(-20, 345, 8))
        self.assertEqual(len(left_to_right), 1)
        self.assertLess(abs(left_to_right[0] - 160), 80)

    def test_reversed_belt_needs_no_setting(self):
        right_to_left = self.run_pass(range(340, -25, -8))
        self.assertEqual(len(right_to_left), 1)
        self.assertLess(abs(right_to_left[0] - 160), 80)

    def test_two_objects_give_two_photos(self):
        fired = self.run_pass(list(range(-20, 345, 8)) + list(range(-20, 345, 8)))
        self.assertEqual(len(fired), 2)

    def test_empty_belt_never_fires(self):
        self.assertEqual(self.run_pass([None] * 100), [])


class SavingTests(unittest.TestCase):
    def test_class_names_are_plain_ascii(self):
        for good in ("bottle", "red_cap", "Part-2"):
            self.assertTrue(CLASS_NAME_PATTERN.match(good), good)
        for bad in ("", "ขวด", "red cap", "a/b", "_x", "CON?"):
            self.assertFalse(CLASS_NAME_PATTERN.match(bad), bad)

    def test_saves_into_a_folder_with_thai_in_its_path(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ภาพสายพาน" / "x.jpg"
            path.parent.mkdir()
            save_jpeg(path, belt_frame(100))
            self.assertEqual(cv2.imdecode(np.fromfile(path, np.uint8), 1).shape, (120, 320, 3))


if __name__ == "__main__":
    unittest.main()
