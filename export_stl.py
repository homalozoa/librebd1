"""Build all BD-1 parts and write one STL per part (BD1.FCStd with colours comes from preview_gui.py).

Run: freecadcmd export_stl.py   (BD1_HEIGHT=316 for life size; default 190 mm head top)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.insert(0, HERE)

import FreeCAD as App
import Mesh

import bd1_model

out = os.path.join(HERE, "stl")
os.makedirs(out, exist_ok=True)
doc = bd1_model.build_document()
for obj in doc.Objects:
    shape = obj.Shape
    bb = shape.BoundBox
    mesh = Mesh.Mesh(shape.tessellate(0.05))
    mesh.write(os.path.join(out, obj.Name + ".stl"))
    print(f"{obj.Name:18s} valid={shape.isValid()} solids={len(shape.Solids)} "
          f"vol={shape.Volume/1000:7.1f}cm3 size={bb.XLength:.0f}x{bb.YLength:.0f}x{bb.ZLength:.0f}mm")
