"""Build the student package: Lab9_ConveyorCapture/dist/ConveyorCapture_Student.zip

    python Lab9_ConveyorCapture\\scripts\\build_package.py

The ZIP holds one folder, ConveyorCapture/, with the manual and two batch files
at the top so students only ever double-click there; the code sits in app/.
"""

import base64
import re
import sys
import zipfile
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
DIST = LAB / "dist"
TARGET = DIST / "ConveyorCapture_Student.zip"
TOP = "ConveyorCapture"

FILES = {
    "Manual.html": LAB / "package" / "Manual.html",
    "START_CAPTURE.bat": LAB / "package" / "START_CAPTURE.bat",
    "MAKE_ZIP.bat": LAB / "package" / "MAKE_ZIP.bat",
    "app/capture_gui.py": LAB / "scripts" / "capture_gui.py",
    "app/make_zip.py": LAB / "scripts" / "make_zip.py",
    "app/requirements.txt": LAB / "requirements_capture_gui.txt",
}


def inline_images(html_bytes):
    """Embed images/<name> as data: URIs so Manual.html is a single file."""
    html = html_bytes.decode("utf-8")

    def embed(match):
        image = LAB / "package" / "images" / match.group(1)
        mime = "image/jpeg" if image.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        data = base64.b64encode(image.read_bytes()).decode("ascii")
        return f'src="data:{mime};base64,{data}"'

    html = re.sub(r'src="images/([^"]+)"', embed, html)
    if "images/" in html:
        raise ValueError("Manual.html still refers to images/ after inlining")
    return html.encode("utf-8")


def main():
    missing = [str(path) for path in FILES.values() if not path.is_file()]
    if missing:
        print("[ERROR] Missing:", *missing, sep="\n  ")
        return 1
    DIST.mkdir(exist_ok=True)
    with zipfile.ZipFile(TARGET, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, source in FILES.items():
            data = source.read_bytes()
            if name == "Manual.html":
                data = inline_images(data)
            if name.endswith(".bat"):
                # cmd.exe misreads labels and goto in LF-only batch files.
                data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            archive.writestr(f"{TOP}/{name}", data)
            print(f"  {TOP}/{name:<22} {len(data) / 1024:>7.1f} KB")
    print(f"Wrote {TARGET} ({TARGET.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
