"""Render every part in its print orientation: images/print_layout_<n>.png.

Run: /Applications/FreeCAD.app/Contents/Resources/bin/python -I render_print_layout.py

Each STL stays at its assembly position, so every part is turned onto the bed here: of
the six directions that can point up, the one with the least overhang wins (see
orient()). The grey slab is the bed; the label gives the print height and the overhang
area (downward faces steeper than 45 degrees that are not on the bed), so supports
show up before slicing.
"""
import glob
import os
import re
import struct

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images")

COLS = 6
ROWS = 4


def load(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[80:84])[0]
    if 84 + 50 * n == len(b):
        a = np.frombuffer(b, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n, offset=84)
        return a["v"].astype(float)
    v = re.findall(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", b.decode("ascii", "ignore"))
    return np.array(v, dtype=float).reshape(-1, 3, 3)


def normals(t):
    c = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ln = np.linalg.norm(c, axis=1)
    return c / np.maximum(ln, 1e-12)[:, None], ln / 2


def rot_matrix(ax, sign):
    """3x3 matrix that turns model axis `ax` (direction `sign`) to point up (+Z)."""
    others = [i for i in range(3) if i != ax]
    m = np.zeros((3, 3))
    m[2, ax] = sign
    m[0, others[0]] = 1
    m[1, others[1]] = 1
    if np.linalg.det(m) < 0:
        m[1, others[1]] = -1
    return m


def turn(t, ax, sign):
    """Rotate so model axis `ax` (direction `sign`) points up, with the bottom on z = 0."""
    r = t @ rot_matrix(ax, sign).T
    r[:, :, 2] -= r[:, :, 2].min()
    return r


def orient(name, t):
    """Pick the up direction (of 6) with the least overhang, then the lowest part.

    Score = overhang area (mm^2) + 5 * height (mm), so a flat plate lies flat and a
    tall part only stands when lying down would need far more support.
    """
    best = None
    for ax in range(3):
        for sign in (1, -1):
            r = turn(t, ax, sign)
            oh, _ = overhang(r)
            score = oh + 5 * r[:, :, 2].max()
            if best is None or score < best[0]:
                best = (score, r, ax, sign)
    return best[1], best[2], best[3]


def overhang(t):
    n, area = normals(t)
    mid = t[:, :, 2].mean(1)
    bad = (n[:, 2] < -0.707) & (mid > 0.3)
    return area[bad].sum(), area.sum()


def draw(ax, t, color):
    az, el = np.radians(-40), np.radians(28)
    ca, sa, ce, se = np.cos(az), np.sin(az), np.cos(el), np.sin(el)
    rot = np.array([[ca, -sa, 0], [sa * se, ca * se, ce], [sa * ce, ca * ce, -se]])  # screen x, screen y, depth
    p = t @ rot.T
    n, _ = normals(t)
    light = np.array([0.3, -0.5, 0.8])
    shade = 0.45 + 0.55 * np.clip(n @ (light / np.linalg.norm(light)), 0, 1)
    order = np.argsort(p[:, :, 2].mean(1))[::-1]
    polys = p[order][:, :, :2]
    cols = np.clip(np.array(color)[None, :] * shade[order][:, None], 0, 1)
    # bed slab under the part
    b = t.reshape(-1, 3)
    pad = max(b[:, 0].ptp(), b[:, 1].ptp()) * 0.15 + 2
    x0, x1, y0, y1 = b[:, 0].min() - pad, b[:, 0].max() + pad, b[:, 1].min() - pad, b[:, 1].max() + pad
    bed = np.array([[x0, y0, 0], [x1, y0, 0], [x1, y1, 0], [x0, y1, 0]]) @ rot.T
    ax.add_collection(PolyCollection([bed[:, :2]], facecolors="#d9d9d9", edgecolors="none"))
    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="none", linewidths=0))
    allp = np.vstack([bed[:, :2], p.reshape(-1, 3)[:, :2]])
    lo, hi = allp.min(0), allp.max(0)
    c, half = (lo + hi) / 2, (hi - lo).max() / 2 * 1.05
    ax.set_xlim(c[0] - half, c[0] + half)
    ax.set_ylim(c[1] - half, c[1] + half)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sorted(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(HERE, "stl", "*.stl")))
    count = {}
    for n in names:
        base = re.sub(r"_(left|right)$", "", n)
        count[base] = count.get(base, 0) + 1
    shown = [n for n in names if not n.endswith("_right") or re.sub(r"_right$", "_left", n) not in names]
    palette = {"paint": (0.77, 0.04, 0.03), "lens": (0.39, 0.52, 0.6), "stand": (0.2, 0.21, 0.23)}
    per = COLS * ROWS
    report = []
    for page in range(0, len(shown), per):
        fig, axes = plt.subplots(ROWS, COLS, figsize=(COLS * 3.2, ROWS * 3.5))
        for a in axes.flat:
            a.axis("off")
        for a, n in zip(axes.flat, shown[page:page + per]):
            t, axis_i, sign = orient(n, load(os.path.join(HERE, "stl", n + ".stl")))
            oh, tot = overhang(t)
            h = t[:, :, 2].max()
            base = re.sub(r"_(left|right)$", "", n)
            key = next((k for k in palette if n.startswith(k)), None)
            draw(a, t, palette.get(key, (0.72, 0.74, 0.66)))
            a.set_title(f"{base} x{count[base]}\nheight {h:.1f} mm, overhang {oh:.0f} mm²", fontsize=8)
            report.append((n, "xyz"[axis_i], sign, h, oh, tot))
        fig.tight_layout()
        path = os.path.join(OUT, f"print_layout_{page // per + 1}.png")
        fig.savefig(path, dpi=110)
        plt.close(fig)
        print("wrote", path)
    print(f"{'part':28s} up  sign height overhang_mm2")
    for n, a, s, h, oh, tot in report:
        print(f"{n:28s} {a}   {s:+d}   {h:6.1f} {oh:8.0f}")


if __name__ == "__main__":
    main()
