"""Compare surface relief of the model and the reference mesh from six directions.

Run: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd depth_diff.py
For each of +x (front), -x (back), +y (left), -y (right), +z (top), -z (bottom)
it rasterises the outermost surface of both meshes into a height map, then
writes views/depth_<dir>.png (red = model stands out, blue = reference stands
out, grey = within TOL) plus the raw height maps in views/depth_<dir>.npz, and
prints the largest differing regions, in mm. Pass direction names to run only those.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image
from scipy import ndimage

import bd1_model
from heightmap import heightmap, reference

RES = 0.5          # mm per pixel
TOL = 1.0          # differences below this are ignored
MIN_AREA = 8.0     # mm2; smaller regions are not listed
# direction: (depth axis, sign, image-right axis, image-up axis)
DIRS = {
    "front": (0, 1, 1, 2), "back": (0, -1, 1, 2),
    "left": (1, 1, 0, 2), "right": (1, -1, 0, 2),
    "top": (2, 1, 1, 0), "bottom": (2, -1, 1, 0),
}
NAMES = "xyz"


def tessellate(parts):
    tris = []
    for _, shape, _, _ in parts:
        pts, idx = shape.tessellate(0.05 * bd1_model.K + 0.02)
        p = np.array([[v.x, v.y, v.z] for v in pts])
        tris.append(p[np.array(idx)])
    return np.concatenate(tris)


def main():
    model = tessellate([p for p in bd1_model.parts() if p[0] != "stand"])
    ref = reference()
    both = np.concatenate([model.reshape(-1, 3), ref.reshape(-1, 3)])
    lo, hi = both.min(0) - 1, both.max(0) + 1
    out = os.path.join(HERE, "views")
    # freecadcmd passes its own arguments too, so pick out the direction names.
    only = [a for a in sys.argv[1:] if a in DIRS] or list(DIRS)
    for name in only:
        ax, sign, ua, va = DIRS[name]
        box = (lo[ua], hi[ua], lo[va], hi[va])
        hm = heightmap(model, ax, sign, ua, va, box, RES)
        hr = heightmap(ref, ax, sign, ua, va, box, RES)
        both_in = np.isfinite(hm) & np.isfinite(hr)
        diff = np.where(both_in, hm - hr, 0.0)
        img = np.full(hm.shape + (3,), 255, np.uint8)
        img[np.isfinite(hm) | np.isfinite(hr)] = (200, 200, 200)
        img[np.isfinite(hm) & ~np.isfinite(hr)] = (255, 150, 150)
        img[~np.isfinite(hm) & np.isfinite(hr)] = (150, 170, 255)
        k = np.clip(np.abs(diff) / 6.0, 0, 1)
        red = diff > TOL
        blue = diff < -TOL
        img[red] = np.stack([np.full(red.sum(), 220), 200 - 160 * k[red], 200 - 160 * k[red]], 1)
        img[blue] = np.stack([200 - 160 * k[blue], 200 - 120 * k[blue], np.full(blue.sum(), 230)], 1)
        Image.fromarray(img).save(os.path.join(out, f"depth_{name}.png"))
        np.savez_compressed(os.path.join(out, f"depth_{name}.npz"), model=hm, ref=hr, box=np.array(box))
        print(f"== {name}: depth along {'+' if sign > 0 else '-'}{NAMES[ax]}, image right {NAMES[ua]}, up {NAMES[va]}")
        regions = []
        for label, mask in (("model sticks out", red), ("reference sticks out", blue)):
            lab, n = ndimage.label(mask)
            for i in range(1, n + 1):
                m = lab == i
                area = m.sum() * RES * RES
                if area < MIN_AREA:
                    continue
                rr, cc = np.nonzero(m)
                u = box[0] + (cc + 0.5) * RES
                v = box[3] - (rr + 0.5) * RES
                d = diff[m]
                regions.append((area * np.abs(d).mean(), label, area, u.min(), u.max(), v.min(), v.max(),
                                np.abs(d).mean(), np.abs(d).max()))
        regions.sort(reverse=True)
        for _, label, area, u0, u1, v0, v1, dm, dx in regions[:10]:
            print(f"  {label:21s} {area:6.0f} mm2  {NAMES[ua]} {u0:6.1f}..{u1:6.1f}  {NAMES[va]} {v0:6.1f}..{v1:6.1f}"
                  f"  mean {dm:4.1f} max {dx:4.1f} mm")


main()
