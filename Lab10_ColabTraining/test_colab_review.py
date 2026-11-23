import io
import json
import shutil
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import torch
import ultralytics
from PIL import Image


NOTEBOOK = Path(__file__).with_name("colab_train_conveyor.ipynb")


class FakeDetector:
    def __init__(self, _model):
        self.prompts = []

    def set_classes(self, names):
        self.prompts.append(names)

    def predict(self, **_kwargs):
        coordinates = torch.tensor([[10, 10, 60, 40]])
        return [types.SimpleNamespace(boxes=types.SimpleNamespace(xyxy=coordinates))]


class ReviewWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive_path = self.root / "images.zip"
        image_bytes = io.BytesIO()
        Image.new("RGB", (100, 50), "white").save(image_bytes, format="JPEG")
        with zipfile.ZipFile(self.archive_path, "w") as archive:
            for name in ("bottle/a.jpg", "bottle/b.jpg", "bottle/c.jpg"):
                archive.writestr(name, image_bytes.getvalue())

        notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        self.cells = ["".join(cell["source"]) for cell in notebook["cells"]]
        self.scope = {
            "MODE": "raw",
            "RAW_ZIP": self.archive_path,
            "Path": Path,
            "PROMPT_OVERRIDES": {"bottle": "plastic bottle"},
            "AUTO_CONFIDENCE": 0.15,
        }
        colab = types.ModuleType("google.colab")
        colab.output = types.SimpleNamespace(enable_custom_widget_manager=lambda: None)
        self.patches = [
            patch.dict("sys.modules", {"google.colab": colab}),
            patch.object(ultralytics, "YOLO", FakeDetector),
            patch.object(torch.cuda, "is_available", return_value=True),
            patch("IPython.display.display"),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def run_cell(self, index):
        source = self.cells[index].replace(
            'Path("/content/drive/MyDrive/conveyor_reviews")',
            f"Path({str(self.root / 'reviews')!r})",
        )
        exec(compile(source, f"notebook-cell-{index}", "exec"), self.scope)

    def test_review_gate_resume_and_yolo_export(self):
        self.run_cell(5)
        self.addCleanup(
            shutil.rmtree, self.scope["raw_dir"]
        )
        self.run_cell(6)
        self.assertEqual(self.scope["detector"].prompts, [["plastic bottle"]])
        self.scope["save_review"]()
        self.assertEqual(sum(self.scope["review_path"](p).is_file() for p in self.scope["raw_images"]), 1)

        with self.assertRaisesRegex(ValueError, "2"):
            self.run_cell(8)

        self.run_cell(6)
        self.assertEqual(self.scope["state"]["index"], 1)
        self.scope["box_widget"].bboxes = []
        with self.assertRaises(ValueError):
            self.scope["save_review"]()
        self.scope["empty_confirm"].value = True
        self.scope["save_review"]()
        self.scope["save_review"]()

        self.run_cell(8)
        self.addCleanup(
            shutil.rmtree, self.scope["build_dir"]
        )
        self.addCleanup(lambda: self.scope["DATASET_ZIP"].unlink(missing_ok=True))
        with zipfile.ZipFile(self.scope["DATASET_ZIP"]) as archive:
            labels = {
                name: archive.read(name).decode("utf-8")
                for name in archive.namelist()
                if name.endswith(".txt")
            }
        self.assertEqual(len(labels), 3)
        self.assertEqual(sum(not value for value in labels.values()), 1)
        self.assertIn("0 0.35000000 0.50000000 0.50000000 0.60000000", [value.strip() for value in labels.values()])

        self.run_cell(10)
        self.addCleanup(
            shutil.rmtree, self.scope["EXTRACT_DIR"]
        )
        self.assertEqual(self.scope["box_counts"], {"bottle": 2})


if __name__ == "__main__":
    unittest.main()
