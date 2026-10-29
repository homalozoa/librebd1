"""Rasterise the outermost surface of a triangle mesh into a height map.

Used by depth_diff.py and for measuring details on the reference mesh. Pure numpy,
so it runs under the FreeCAD Python as well as freecadcmd.
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def heightmap(tris, ax, sign, ua, va, box, res=0.5):
    """Max of sign * coordinate[ax] over each (ua, va) pixel; -inf where nothing is hit.

    tris: (n, 3, 3) triangles. box: (u0, u1, v0, v1) in mm. Row 0 is the top (v1).
    """
    u0, u1, v0, v1 = box
    nu, nv = int(np.ceil((u1 - u0) / res)), int(np.ceil((v1 - v0) / res))
    H = np.full((nv, nu), -np.inf)
    cu = (tris[:, :, ua] - u0) / res
    cv = (v1 - tris[:, :, va]) / res
    dd = tris[:, :, ax] * sign
    for t in range(len(tris)):
        x, y, z = cu[t], cv[t], dd[t]
        a0, a1 = max(int(x.min()), 0), min(int(np.ceil(x.max())), nu - 1)
        b0, b1 = max(int(y.min()), 0), min(int(np.ceil(y.max())), nv - 1)
        if a1 < a0 or b1 < b0:
            continue
        den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(den) < 1e-12:
            continue
        uu, vv = np.meshgrid(np.arange(a0, a1 + 1) + 0.5, np.arange(b0, b1 + 1) + 0.5)
        l0 = ((y[1] - y[2]) * (uu - x[2]) + (x[2] - x[1]) * (vv - y[2])) / den
        l1 = ((y[2] - y[0]) * (uu - x[2]) + (x[0] - x[2]) * (vv - y[2])) / den
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if inside.any():
            zz = np.where(inside, l0 * z[0] + l1 * z[1] + l2 * z[2], -np.inf)
            sub = H[b0:b1 + 1, a0:a1 + 1]
            np.maximum(sub, zz, out=sub)
    return H


def pixel_centres(H, box, res=0.5):
    """(U, V) grids of pixel centre coordinates for a height map made with the same box and res."""
    u0, _, _, v1 = box
    return np.meshgrid(u0 + (np.arange(H.shape[1]) + 0.5) * res, v1 - (np.arange(H.shape[0]) + 0.5) * res)


def reference(names=None):
    """Reference mesh from ref/bd1_ref.npz: all parts, or just the named ones, as one triangle array."""
    data = np.load(os.path.join(HERE, "ref", "bd1_ref.npz"))
    keys = [k for k in data.files if not k.endswith("#rgb")]
    return np.concatenate([data[k] for k in (names or keys)])
