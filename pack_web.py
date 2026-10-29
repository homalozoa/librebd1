"""Pack the part STLs into compact web data for the web app in web/: web/public/data/bd1.bin + parts.json.

Run: /Applications/FreeCAD.app/Contents/Resources/bin/python -I pack_web.py

The binary holds, per part, welded int16 vertices (quantised to the part's own bounding box)
and uint32 triangle indices. parts.json says where each part lives in the file, its colour,
and its print pose (rotation + position on a 256 x 256 bed) from render_print_layout.orient().
"""
import glob
import json
import os
import re

import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # -I drops the script's folder from the path
import render_print_layout as R  # noqa: E402
DATA = os.path.join(HERE, "web", "public", "data")
BED = 256.0
MARGIN = 6.0

# colours as in the README table; first matching prefix wins
COLOURS = [
    ("antenna_collar", "#424242"), ("antenna", "#C9CFB0"), ("chest_plate", "#999996"), ("chest_tab", "#7A2B26"),
    ("ear_centre", "#82827D"), ("ear", "#B2A696"), ("eye_band", "#C40A08"), ("eye_ring_left", "#B8BAB0"),
    ("eye_ring_right", "#5E3330"), ("foot_front", "#B2B59E"), ("foot_heel", "#595952"), ("head_light", "#52A624"),
    ("head_shell", "#C9CFB0"), ("head_top_band", "#999996"), ("knee_cap", "#82827D"), ("lens_left", "#B2B5B2"),
    ("lens_right", "#638599"), ("neck", "#C9CFB0"), ("paint_left_hood_grey", "#999996"), ("paint_right_hood_grey", "#999996"),
    ("paint_left_top_edge", "#999996"), ("paint_right_top_edge", "#999996"), ("paint_right_panel_dot", "#C40A08"),
    ("paint_right_panel", "#999996"), ("paint_", "#C40A08"), ("shin_plate", "#7A2B26"), ("shin_", "#80786B"),
    ("stand", "#33363B"), ("thigh_channel_floor", "#593D36"), ("thigh_channel_tip", "#593D36"), ("thigh_channel", "#7A2B26"),
    ("thigh_piston", "#82827D"), ("thigh_rod", "#82827D"), ("thigh_", "#B2A696"), ("torso", "#C9CFB0"),
]


def colour(name):
    return next(c for p, c in COLOURS if name.startswith(p))


def weld(tris, step=0.005):
    flat = np.round(tris.reshape(-1, 3) / step).astype(np.int64)
    uniq, inv = np.unique(flat, axis=0, return_inverse=True)
    idx = inv.reshape(-1, 3)
    keep = (idx[:, 0] != idx[:, 1]) & (idx[:, 1] != idx[:, 2]) & (idx[:, 0] != idx[:, 2])
    return uniq.astype(float) * step, idx[keep]


def main():
    os.makedirs(DATA, exist_ok=True)
    names = sorted(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(HERE, "stl", "*.stl")))
    blob = bytearray()
    parts = []
    for n in names:
        t = R.load(os.path.join(HERE, "stl", n + ".stl"))
        v, idx = weld(t)
        lo, hi = v.min(0), v.max(0)
        scale = np.maximum(hi - lo, 1e-6) / 65535.0
        q = np.round((v - lo) / scale).astype(np.uint16)
        while len(blob) % 4:
            blob.append(0)
        voff = len(blob)
        blob += q.tobytes()
        while len(blob) % 4:
            blob.append(0)
        ioff = len(blob)
        blob += idx.astype(np.uint32).tobytes()
        # print pose
        r, ax, sign = R.orient(n, t)
        m = R.rot_matrix(ax, sign)
        rt = t @ m.T
        dz = -rt[:, :, 2].min()
        oh, _ = R.overhang(r)
        ext = r.reshape(-1, 3).max(0) - r.reshape(-1, 3).min(0)
        parts.append(dict(
            name=n, colour=colour(n), lo=lo.round(4).tolist(), scale=scale.tolist(), nv=len(v), nt=len(idx),
            voff=voff, ioff=ioff, centre=((lo + hi) / 2).round(3).tolist(),
            rot=m.round(6).tolist(), dz=round(float(dz), 4), foot=[round(float(ext[0]), 2), round(float(ext[1]), 2)],
            height=round(float(ext[2]), 2), overhang=round(float(oh), 1),
            rotMin=(rt.reshape(-1, 3).min(0)).round(3).tolist(),
        ))
    # pack footprints on 256 x 256 beds, tallest-footprint first, shelf by shelf
    order = sorted(range(len(parts)), key=lambda i: -max(parts[i]["foot"]))
    plates, cx, cy, row_h, plate = [], MARGIN, MARGIN, 0.0, 0
    for i in order:
        w, d = parts[i]["foot"]
        if cx + w + MARGIN > BED:
            cx, cy, row_h = MARGIN, cy + row_h + 4, 0.0
        if cy + d + MARGIN > BED:
            plate += 1
            cx, cy, row_h = MARGIN, MARGIN, 0.0
        parts[i]["plate"] = plate
        parts[i]["bed"] = [round(cx, 2), round(cy, 2)]
        cx += w + 4
        row_h = max(row_h, d)
    for p in parts:
        # world position of the rotated part's min corner = plate origin + bed offset
        p["bed"].append(0.0)
    open(os.path.join(DATA, "bd1.bin"), "wb").write(blob)
    json.dump(dict(bed=BED, plates=plate + 1, parts=parts), open(os.path.join(DATA, "parts.json"), "w"), separators=(",", ":"))
    print(f"{len(parts)} parts, {len(blob) / 1e6:.2f} MB bin, {plate + 1} plates")


if __name__ == "__main__":
    main()
