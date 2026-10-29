"""Overlay reference images on the model's orthographic renders and measure the gap.

Run render_views.py first, then:
  /Applications/FreeCAD.app/Contents/Resources/bin/python compare.py [front side top]

For each view it reads ref/<view>.(png|jpg|jpeg|webp). If the background is not
plain, also give ref/<view>_mask.png (black BD-1 on white) and it is used as is.
With no reference image but a reference mesh render (views/ref_<view>_mask.png
from glb_ref.py + render_views.py), the two renders are placed by their world
coordinates instead, so the comparison needs no fitting and is exact.
Outputs, in views/:
  <view>_overlay.png  grey = both, red = model only, blue = reference only
  <view>_ghost.png    reference photo with the model render laid over at 50 %
and prints IoU plus the 5 mm bands where the outlines differ most, in mm.
"""
import json
import os
import sys
import warnings

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWS_DIR = os.path.join(HERE, "views")
REF_DIR = os.environ.get("BD1_REF_DIR", os.path.join(HERE, "ref"))
BAND_MM = 5.0
REPORT_MM = 1.0       # only list bands whose edges differ by more than this


def load_mask(path):
    return np.array(Image.open(path).convert("L")) < 128


def ref_mask(view, img):
    own = os.path.join(REF_DIR, f"{view}_mask.png")
    if os.path.exists(own):
        return load_mask(own)
    a = np.asarray(img.convert("RGB"), float)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    dist = np.linalg.norm(a - bg, axis=2)
    m = dist > max(30.0, 3 * np.median(np.linalg.norm(border - bg, axis=1)))
    m = ndimage.binary_opening(m, iterations=1)
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=2))
    lab, n = ndimage.label(m)
    if n > 1:
        # Keep pieces that are at least 2 % of the largest, so thin antennas
        # and separated feet survive but specks do not.
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.flatnonzero(sizes >= 0.02 * sizes.max()))
    return m


def crop(m):
    ys, xs = np.nonzero(m)
    return (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1)


def resize_mask(m, scale):
    h, w = m.shape
    im = Image.fromarray((m * 255).astype(np.uint8))
    im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.BILINEAR)
    return np.array(im) > 127


def paste(canvas_shape, m, dy, dx):
    out = np.zeros(canvas_shape, bool)
    H, W = canvas_shape
    h, w = m.shape
    y0, x0 = max(dy, 0), max(dx, 0)
    y1, x1 = min(dy + h, H), min(dx + w, W)
    if y1 > y0 and x1 > x0:
        out[y0:y1, x0:x1] = m[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    return out


def iou(a, b):
    u = np.logical_or(a, b).sum()
    return np.logical_and(a, b).sum() / u if u else 0.0


def fit(model, ref):
    """Scale, mirror and shift the reference onto the model; return best placement."""
    my0, my1, mx0, mx1 = crop(model)
    ry0, ry1, rx0, rx1 = crop(ref)
    ref_c = ref[ry0:ry1, rx0:rx1]
    base = (my1 - my0) / (ry1 - ry0)
    # Coarse search on a downsampled grid, then refine at full resolution.
    best = None
    for flip in (False, True):
        r0 = ref_c[:, ::-1] if flip else ref_c
        for s in np.linspace(0.85, 1.15, 31) * base:
            r = resize_mask(r0, s)
            cy = my0 + (my1 - my0) // 2 - r.shape[0] // 2
            cx = mx0 + (mx1 - mx0) // 2 - r.shape[1] // 2
            for dy in range(-30, 31, 6):
                for dx in range(-30, 31, 6):
                    sc = iou(model[::4, ::4], paste(model.shape, r, cy + dy, cx + dx)[::4, ::4])
                    if best is None or sc > best[0]:
                        best = (sc, flip, s, cy + dy, cx + dx)
    _, flip, s, y, x = best
    r0 = ref_c[:, ::-1] if flip else ref_c
    for s2 in np.linspace(s * 0.99, s * 1.01, 5):
        r = resize_mask(r0, s2)
        for dy in range(-6, 7, 2):
            for dx in range(-6, 7, 2):
                sc = iou(model, paste(model.shape, r, y + dy, x + dx))
                if sc > best[0]:
                    best = (sc, flip, s2, y + dy, x + dx)
    return best, (ry0, ry1, rx0, rx1)


def edges(m, axis):
    """First/last filled pixel per row (axis=1) or column (axis=0); NaN if empty."""
    any_ = m.any(axis=axis)
    first = np.where(any_, m.argmax(axis=axis), np.nan)
    last = np.where(any_, m.shape[axis] - 1 - np.flip(m, axis=axis).argmax(axis=axis), np.nan)
    return first, last


def band_report(model, ref, px_per_mm, axis, label):
    """Compare outline edges band by band; axis=1 means horizontal bands (rows)."""
    mf, ml = edges(model, axis)
    rf, rl = edges(ref, axis)
    band = int(round(BAND_MM * px_per_mm))
    rows = []
    for i in range(0, len(mf), band):
        sl = slice(i, i + band)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            d_lo = np.nanmean(rf[sl] - mf[sl]) / px_per_mm
            d_hi = np.nanmean(rl[sl] - ml[sl]) / px_per_mm
        if np.isnan(d_lo) and np.isnan(d_hi):
            continue
        worst = np.nanmax(np.abs([d_lo, d_hi]))
        rows.append((worst, i / px_per_mm, d_lo, d_hi))
    rows.sort(reverse=True)
    sides = ("left", "right") if axis == 1 else ("top", "bottom")
    pos = "from top" if axis == 1 else "from left"
    print(f"  {label}: edge offset ref minus model in mm (+ = further right/down)")
    for worst, at, d_lo, d_hi in rows[:6]:
        if worst < REPORT_MM:
            break
        print(f"    {at:6.0f}-{at + BAND_MM:.0f} mm {pos}: {sides[0]} edge {d_lo:+6.1f}, {sides[1]} edge {d_hi:+6.1f}")


def place(mask, info, canvas_u0, canvas_v1, px, shape):
    """Put a render on a shared canvas using its world-space origin."""
    dx = int(round((info["u_min_mm"] - canvas_u0) * px))
    dy = int(round((canvas_v1 - info["v_max_mm"]) * px))
    return paste(shape, mask, dy, dx), dy, dx


def compare_mesh(view, scale):
    px, m = scale["px_per_mm"], scale["margin_px"]
    a, b = scale[view], scale["ref_" + view]
    model = load_mask(os.path.join(VIEWS_DIR, f"{view}_mask.png"))
    ref = load_mask(os.path.join(VIEWS_DIR, f"ref_{view}_mask.png"))
    u0 = min(a["u_min_mm"], b["u_min_mm"])
    v1 = max(a["v_max_mm"], b["v_max_mm"])
    u1 = max(a["u_min_mm"] + a["width_mm"], b["u_min_mm"] + b["width_mm"])
    v0 = min(a["v_max_mm"] - a["height_mm"], b["v_max_mm"] - b["height_mm"])
    shape = (int((v1 - v0) * px) + 2 * m + 2, int((u1 - u0) * px) + 2 * m + 2)
    pm, mdy, mdx = place(model, a, u0, v1, px, shape)
    pr, rdy, rdx = place(ref, b, u0, v1, px, shape)
    score = iou(pm, pr)
    print(f"{view}: IoU {score:.3f} vs reference mesh (model-only "
          f"{np.logical_and(pm, ~pr).sum() / px**2:.0f} mm2, ref-only {np.logical_and(pr, ~pm).sum() / px**2:.0f} mm2)")
    band_report(pm, pr, px, 1, "rows")
    band_report(pm, pr, px, 0, "columns")
    over = np.full(shape + (3,), 255, np.uint8)
    over[pm & pr] = (150, 150, 150)
    over[pm & ~pr] = (220, 40, 40)
    over[pr & ~pm] = (40, 90, 220)
    Image.fromarray(over).save(os.path.join(VIEWS_DIR, f"{view}_overlay.png"))
    canvas_a = Image.new("RGB", shape[::-1], "white")
    canvas_a.paste(Image.open(os.path.join(VIEWS_DIR, f"{view}_color.png")).convert("RGB"), (mdx, mdy))
    canvas_b = Image.new("RGB", shape[::-1], "white")
    canvas_b.paste(Image.open(os.path.join(VIEWS_DIR, f"ref_{view}_color.png")).convert("RGB"), (rdx, rdy))
    Image.blend(canvas_b, canvas_a, 0.5).save(os.path.join(VIEWS_DIR, f"{view}_ghost.png"))


def compare(view, scale):
    ref_path = next((os.path.join(REF_DIR, f"{view}.{e}") for e in ("png", "jpg", "jpeg", "webp")
                     if os.path.exists(os.path.join(REF_DIR, f"{view}.{e}"))), None)
    if ref_path is None:
        if "ref_" + view in scale:
            compare_mesh(view, scale)
        else:
            print(f"{view}: no ref/{view}.png, skipped")
        return
    model = load_mask(os.path.join(VIEWS_DIR, f"{view}_mask.png"))
    img = Image.open(ref_path)
    ref = ref_mask(view, img)
    (score, flip, s, y, x), (ry0, ry1, rx0, rx1) = fit(model, ref)
    ref_c = ref[ry0:ry1, rx0:rx1]
    placed = paste(model.shape, resize_mask(ref_c[:, ::-1] if flip else ref_c, s), y, x)
    px = scale["px_per_mm"]
    print(f"{view}: IoU {score:.3f}  (ref scaled x{s:.3f}{', mirrored' if flip else ''}; "
          f"model-only {np.logical_and(model, ~placed).sum() / px**2:.0f} mm2, "
          f"ref-only {np.logical_and(placed, ~model).sum() / px**2:.0f} mm2)")
    band_report(model, placed, px, 1, "rows")
    band_report(model, placed, px, 0, "columns")

    over = np.full(model.shape + (3,), 255, np.uint8)
    over[model & placed] = (150, 150, 150)
    over[model & ~placed] = (220, 40, 40)
    over[placed & ~model] = (40, 90, 220)
    Image.fromarray(over).save(os.path.join(VIEWS_DIR, f"{view}_overlay.png"))

    photo = img.convert("RGB").crop((rx0, ry0, rx1, ry1))
    if flip:
        photo = photo.transpose(Image.FLIP_LEFT_RIGHT)
    photo = photo.resize((max(1, round(photo.width * s)), max(1, round(photo.height * s))))
    canvas = Image.new("RGB", model.shape[::-1], "white")
    canvas.paste(photo, (x, y))
    render = Image.open(os.path.join(VIEWS_DIR, f"{view}_color.png")).convert("RGB")
    Image.blend(canvas, render, 0.5).save(os.path.join(VIEWS_DIR, f"{view}_ghost.png"))


def main():
    with open(os.path.join(VIEWS_DIR, "scale.json")) as f:
        scale = json.load(f)
    for view in sys.argv[1:] or ("front", "side", "top"):
        compare(view, scale)


if __name__ == "__main__":
    main()
