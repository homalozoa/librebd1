"""Print simplified 2D outlines of reference mesh parts, for pasting into bd1_model.

Run: /Applications/FreeCAD.app/Contents/Resources/bin/python -I ref_profiles.py
Projects each listed mesh from ref/bd1_ref.npz onto a plane, unions the
triangles with shapely and simplifies the outline to TOL mm.
"""
import os
import sys

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 0.5
PLANES = {"xz": (0, 2), "yz": (1, 2), "xy": (0, 1)}
JOBS = [  # (mesh name, plane, optional (axis, lo, hi) slab filter on the dropped axis)
    ("legs.001", "xz", None),
    ("LEG_DT.001", "xz", None),
    ("feet.001", "xz", None),
    ("feet.002", "xz", None),
    ("NECH", "xz", None),
    ("NECH", "yz", None),
    ("HEAD", "xz", None),
]


def outline(tris, plane):
    a, b = PLANES[plane]
    p = tris[:, :, [a, b]]
    area = 0.5 * np.abs((p[:, 1, 0] - p[:, 0, 0]) * (p[:, 2, 1] - p[:, 0, 1])
                        - (p[:, 2, 0] - p[:, 0, 0]) * (p[:, 1, 1] - p[:, 0, 1]))
    polys = [Polygon(t) for t in p[area > 1e-4]]
    u = unary_union(polys).buffer(0.15).buffer(-0.15)
    if u.geom_type == "MultiPolygon":
        u = max(u.geoms, key=lambda g: g.area)
    return Polygon(u.exterior).simplify(TOL)


def main():
    data = np.load(os.path.join(HERE, "ref", "bd1_ref.npz"))
    for name, plane, _ in JOBS:
        poly = outline(data[name], plane)
        pts = [(round(x, 1), round(y, 1)) for x, y in list(poly.exterior.coords)[:-1]]
        print(f"# {name} {plane}: {len(pts)} points, area {poly.area:.0f} mm2")
        print(f"{name.upper().replace('.', '_').replace(' ', '_')}_{plane.upper()} = {pts}")


if __name__ == "__main__":
    sys.exit(main())
