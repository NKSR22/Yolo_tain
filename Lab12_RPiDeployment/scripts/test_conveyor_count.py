import unittest

from conveyor_count import LineCounter

W, H = 640, 480


def box(cx, cy=240, name="bottle", size=60):
    return (cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2, name)


class LineCounterTests(unittest.TestCase):
    def slide(self, counter, xs, name="bottle", cy=240):
        events = []
        for x in xs:
            events += counter.update([box(x, cy, name)], W, H)
        return events

    def test_counts_once_per_pass_and_records_direction(self):
        counter = LineCounter()
        events = self.slide(counter, range(20, 640, 15))
        self.assertEqual([(t.class_name, d) for t, d in events], [("bottle", "+")])
        self.assertEqual(counter.counts, {"bottle": 1})

    def test_reversed_belt_counts_the_other_way(self):
        counter = LineCounter()
        events = self.slide(counter, range(620, 0, -15))
        self.assertEqual([d for _t, d in events], ["-"])

    def test_wobbling_on_the_line_counts_once(self):
        counter = LineCounter()
        self.slide(counter, [300, 315, 330, 318, 325, 340, 360])
        self.assertEqual(counter.counts["bottle"], 1)

    def test_two_objects_side_by_side_are_two_tracks(self):
        counter = LineCounter()
        for x in range(20, 640, 15):
            counter.update([box(x, 120, "bottle"), box(x - 200, 360, "can")], W, H)
        self.assertEqual(counter.counts, {"bottle": 1, "can": 1})

    def test_a_misread_frame_at_the_line_does_not_change_the_class(self):
        counter = LineCounter()
        names = ["can"] * 20 + ["bottle"] + ["can"] * 20
        for x, name in zip(range(20, 640, 15), names):
            counter.update([box(x, name=name)], W, H)
        self.assertEqual(counter.counts, {"can": 1})

    def test_short_dropout_keeps_the_track(self):
        counter = LineCounter()
        for x in range(20, 300, 15):
            counter.update([box(x)], W, H)
        for _ in range(5):
            counter.update([], W, H)
        for x in range(330, 640, 15):
            counter.update([box(x)], W, H)
        self.assertEqual(counter.counts["bottle"], 1)
        self.assertEqual(counter.next_id, 2)

    def test_one_object_after_another_counts_each(self):
        counter = LineCounter()
        for _ in range(3):
            self.slide(counter, range(20, 640, 15))
            for _ in range(15):
                counter.update([], W, H)
        self.assertEqual(counter.counts["bottle"], 3)

    def test_vertical_belt(self):
        counter = LineCounter(axis="y", position=0.5)
        events = []
        for y in range(20, 480, 15):
            events += counter.update([box(320, y)], W, H)
        self.assertEqual([d for _t, d in events], ["+"])


if __name__ == "__main__":
    unittest.main()
