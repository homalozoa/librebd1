"""Orthographic front / side / top renders of the model, without the GUI.

Run: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd render_views.py
Writes views/<view>_color.png (flat-shaded, per-part colours) and
views/<view>_mask.png (black silhouette on white) at PX_PER_MM, plus
views/scale.json. Each image is cropped to the model with a MARGIN_PX border,
so pixel offsets convert straight to mm.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image, ImageDraw

import bd1_model

PX_PER_MM = 6.0
MARGIN_PX = 20
LIGHT = np.array([0.5, 0.3, 0.8]) / np.linalg.norm([0.5, 0.3, 0.8])

# (towards viewer, screen right, screen up) as world unit vectors.
# side: viewer on BD-1's right (-Y), so the face points to the image's right.
VIEWS = {
    "front": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "side": ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
    "top": ((0, 0, 1), (0, -1, 0), (1, 0, 0)),
}


def tessellate(parts):
    """All triangles as (verts[n,3,3], colours[n,3])."""
    tris, cols = [], []
    for _, shape, colour, _ in parts:
        pts, idx = shape.tessellate(0.05 * bd1_model.K + 0.02)
        p = np.array([[v.x, v.y, v.z] for v in pts])
        t = p[np.array(idx)]
        tris.append(t)
        cols.append(np.tile(colour, (len(t), 1)))
    return np.concatenate(tris), np.concatenate(cols)


def render(tris, cols, toward, right, up):
    toward, right, up = (np.array(v, float) for v in (toward, right, up))
    u = tris @ right
    v = tris @ up
    depth = (tris @ toward).mean(axis=1)
    u0, v1 = u.min(), v.max()
    w = int(np.ceil((u.max() - u0) * PX_PER_MM)) + 2 * MARGIN_PX
    h = int(np.ceil((v1 - v.min()) * PX_PER_MM)) + 2 * MARGIN_PX
    px = (u - u0) * PX_PER_MM + MARGIN_PX
    py = (v1 - v) * PX_PER_MM + MARGIN_PX
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    norm = np.linalg.norm(normals, axis=1)
    keep = norm > 1e-9
    normals[keep] /= norm[keep, None]
    # Light fixed to the camera so every view is lit the same way.
    cam_n = np.stack([normals @ right, normals @ up, normals @ toward], axis=1)
    shade = 0.35 + 0.65 * np.abs(cam_n @ LIGHT)
    color = Image.new("RGB", (w, h), "white")
    mask = Image.new("L", (w, h), 255)
    dc, dm = ImageDraw.Draw(color), ImageDraw.Draw(mask)
    for i in np.argsort(depth):  # painter's order: far to near
        poly = list(zip(px[i], py[i]))
        dm.polygon(poly, fill=0)
        if keep[i]:
            c = tuple(int(255 * min(1.0, ch * shade[i])) for ch in cols[i])
            dc.polygon(poly, fill=c)
    return color, mask, {"u_min_mm": float(u0), "v_max_mm": float(v1),
                         "width_mm": float(u.max() - u0), "height_mm": float(v1 - v.min())}


def reference():
    """Triangles of the downloaded reference mesh (ref/bd1_ref.npz from glb_ref.py)."""
    path = os.path.join(HERE, "ref", "bd1_ref.npz")
    if not os.path.exists(path):
        return None
    data = np.load(path)
    names = [k for k in data.files if not k.endswith("#rgb")]
    tris = np.concatenate([data[k] for k in names])
    cols = np.concatenate([data[k + "#rgb"] for k in names])
    return tris, cols


def main():
    out = os.path.join(HERE, "views")
    os.makedirs(out, exist_ok=True)
    # The display stand is not part of BD-1, so it stays out of the comparison.
    sets = {"": tessellate([p for p in bd1_model.parts() if p[0] != "stand"])}
    ref = reference()
    if ref is not None:
        sets["ref_"] = ref
    scale = {"px_per_mm": PX_PER_MM, "margin_px": MARGIN_PX}
    for prefix, (tris, cols) in sets.items():
        for name, axes in VIEWS.items():
            color, mask, info = render(tris, cols, *axes)
            color.save(os.path.join(out, f"{prefix}{name}_color.png"))
            mask.save(os.path.join(out, f"{prefix}{name}_mask.png"))
            scale[prefix + name] = info
            print(f"{prefix}{name}: {info['width_mm']:.1f} x {info['height_mm']:.1f} mm")
    with open(os.path.join(out, "scale.json"), "w") as f:
        json.dump(scale, f, indent=2)


main()
