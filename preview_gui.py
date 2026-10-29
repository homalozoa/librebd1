"""Open in the FreeCAD GUI: build coloured parts, save BD1.FCStd and preview PNGs.

Run: /Applications/FreeCAD.app/Contents/Resources/bin/freecad preview_gui.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.insert(0, HERE)
import FreeCAD as App
import FreeCADGui as Gui
import bd1_model

doc = bd1_model.build_document()
doc.saveAs(os.path.join(HERE, "BD1.FCStd"))
view = Gui.activeDocument().activeView()
# Camera from front-right-above (model faces +X), with world Z kept up.
cam_z = App.Vector(1.0, -0.8, 0.5).normalize()
cam_x = App.Vector(0, 0, 1).cross(cam_z).normalize()
cam_y = cam_z.cross(cam_x)
m = App.Matrix(cam_x.x, cam_y.x, cam_z.x, 0, cam_x.y, cam_y.y, cam_z.y, 0, cam_x.z, cam_y.z, cam_z.z, 0)
# The first camera change after the window opens can be dropped, so repeat.
for _ in range(2):
    Gui.updateGui(); view.setCameraOrientation(App.Rotation(m)); view.fitAll()
view.saveImage(os.path.join(HERE, "preview.png"), 1200, 1000, "White")
if os.environ.get("BD1_QUIT"):
    Gui.getMainWindow().close()
