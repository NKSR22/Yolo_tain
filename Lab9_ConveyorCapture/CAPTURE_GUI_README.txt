Conveyor Image Capture - Windows portable package
==================================================

The conveyor runs on its own (a switch turns it on and sets its direction).
This program only watches the camera and saves one photo per object that passes.

FIRST RUN
---------
1. Install Python 3 from python.org. Enable the Python launcher or "Add Python to PATH".
   The standard Windows installer includes tkinter; do not disable Tcl/Tk.
2. Extract the complete ZIP folder to a writable location.
3. Connect the USB camera and fix it so it does not move.
4. Double-click scripts\run_capture_gui_portable.bat.
   The first launch creates a local .venv and installs opencv-python and Pillow.
   Internet access is needed for the initial package installation.

USING THE APP
-------------
1. Open camera. Change Camera index if Windows assigned a different camera.
2. Draw capture area: drag a box across the belt in the middle of the view.
3. Type a Class name in English letters/digits/_/- (for example bottle, red_cap).
4. Switch the belt on, keep the box empty, and click Start auto capture.
   The box turns yellow while the program learns the empty running belt.
5. Place objects on the belt one at a time. When an object reaches the middle
   of the box, the box turns red and one full-frame JPG is saved.
6. To change class: Stop auto capture, edit Class name, Start auto capture.
   Capture now (or the Space key) saves the current frame immediately.

If photos are taken with no object present, raise Motion threshold %. The status
bar shows the current motion % - on an empty running belt it should stay near 0.

Images are saved in captured_images\<class>\ next to this README. The class name
becomes the YOLO class name later; this app does not create bounding boxes.

To pack the images for Google Colab, zip the class folders so the ZIP contains
<class>\<image>.jpg, name it conveyor_images.zip and upload it to My Drive.

SAFETY
------
Keep hands clear of the running belt. Use the conveyor's own switch or emergency
stop to stop it; this program cannot stop the belt.
