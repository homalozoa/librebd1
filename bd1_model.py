"""BD-1 (Star Wars Jedi: Fallen Order) modular fan model for FreeCAD 1.x.

Proportions are measured from the reference mesh in
bd-1-droid-star-wars-jedi-fallen-order/ (see glb_ref.py), at the size where the
top of the head shell is 190 mm. Every colour region is its own part so each
can be printed in its own filament or painted separately, then joined with
3 mm pins (steel/aluminium rod or M3 screws) and glue.

Axes: X forward (face), Y to BD-1's left, Z up, feet on Z=0. Units mm.
BD1_HEIGHT (head-top height in mm, default 190) scales the body; pin holes and
glue gaps stay at a fixed size so the same hardware fits at any size.
"""
import math
import os

import FreeCAD as App
import Part

V = App.Vector
HEIGHT = float(os.environ.get("BD1_HEIGHT", "190"))
K = HEIGHT / 190.0
PIN_D = 3.0          # pin diameter (hardware)
PIN_HOLE = 3.3       # hole for a pin that should turn freely
ROD_HOLE = 2.3       # hole for a 2 mm brass antenna rod
GLUE_GAP = 0.2       # clearance per side for parts that slot into pockets
INLAY = 1.0          # depth of colour inlay pockets

# Paint colours (RGB 0..1), taken from the reference textures.
WHITE = (0.88, 0.87, 0.78)
GREY = (0.55, 0.56, 0.58)
DARK = (0.20, 0.21, 0.23)
RED = (0.72, 0.10, 0.10)
BLUE = (0.15, 0.40, 0.65)
LENS_GREY = (0.78, 0.79, 0.80)
GREEN = (0.30, 0.75, 0.30)


def s(x):
    return x * K


def g():
    """Glue gap in model units, so it stays GLUE_GAP mm after scaling."""
    return GLUE_GAP / K


# ---------------------------------------------------------------- primitives
def prism_xz(pts, y0, y1):
    """Polygon in the XZ plane, extruded from y0 to y1."""
    w = Part.makePolygon([V(s(x), s(y0), s(z)) for x, z in pts] + [V(s(pts[0][0]), s(y0), s(pts[0][1]))])
    return Part.Face(w).extrude(V(0, s(y1 - y0), 0))


def prism_yz(pts, x0, x1):
    """Polygon in the YZ plane, extruded from x0 to x1."""
    w = Part.makePolygon([V(s(x0), s(y), s(z)) for y, z in pts] + [V(s(x0), s(pts[0][0]), s(pts[0][1]))])
    return Part.Face(w).extrude(V(s(x1 - x0), 0, 0))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(s(x1 - x0), s(y1 - y0), s(z1 - z0), V(s(x0), s(y0), s(z0)))


def cyl_y(x, z, r, y0, y1, fixed_r=False):
    lo, hi = min(y0, y1), max(y0, y1)
    return Part.makeCylinder(r if fixed_r else s(r), s(hi - lo), V(s(x), s(lo), s(z)), V(0, 1, 0))


def cyl_x(y, z, r, x0, x1):
    return Part.makeCylinder(s(r), s(x1 - x0), V(s(x0), s(y), s(z)), V(1, 0, 0))


def pin_hole_y(x, z, y0, y1):
    lo, hi = min(y0, y1) - 1, max(y0, y1) + 1
    return cyl_y(x, z, PIN_HOLE / 2, lo, hi, fixed_r=True)


def capsule_xz(c1, r1, c2, r2, y0, y1):
    """Convex hull of two circles in the XZ plane, extruded along Y (a leg link)."""
    (x1, z1), (x2, z2) = c1, c2
    d = math.hypot(x2 - x1, z2 - z1)
    base = math.atan2(z2 - z1, x2 - x1)
    a = math.acos((r1 - r2) / d)
    pts = []
    for sgn in (1, -1):
        ang = base + sgn * a
        pts.append(((x1 + r1 * math.cos(ang), z1 + r1 * math.sin(ang)),
                    (x2 + r2 * math.cos(ang), z2 + r2 * math.sin(ang))))
    poly = [pts[0][0], pts[0][1], pts[1][1], pts[1][0]]
    lo, hi = min(y0, y1), max(y0, y1)
    shape = prism_xz(poly, lo, hi).fuse([cyl_y(x1, z1, r1, lo, hi), cyl_y(x2, z2, r2, lo, hi)])
    return shape.removeSplitter()


def try_fillet(shape, r, edges=None):
    try:
        return shape.makeFillet(s(r), edges or shape.Edges)
    except Exception:
        return shape


def along(c1, c2, t):
    return (c1[0] + (c2[0] - c1[0]) * t, c1[1] + (c2[1] - c1[1]) * t)


# ---------------------------------------------------------------- head
HEAD_Y = 55.5
HEAD_Z0, HEAD_Z1 = 151.6, 189.5   # underside, and top face height where the outlines agree
HEAD_SIDE = [(-60.7, 152.4), (52.0, HEAD_Z0), (52.0, HEAD_Z1), (-47.4, HEAD_Z1)]   # back slope from [0] to [3]
# Head outlines traced from the reference mesh (ref_profiles.py), chin tabs left out.
HEAD_XZ = [(-60.7, 152.4), (-48.0, 188.2), (-46.8, 189.9), (51.3, 190.0), (52.0, 189.5), (52.2, 182.8),
           (75.3, 182.8), (76.7, 182.3), (69.9, 152.1), (34.3, 151.6)]
HEAD_YZ = [(-55.5, 156.7), (-55.5, 185.2), (-54.2, 188.2), (-51.5, 189.5), (51.5, 189.5), (54.2, 188.2),
           (55.5, 185.2), (55.5, 156.7), (52.9, 152.2), (48.3, 151.6), (-48.3, 151.6), (-52.9, 152.2)]
HEAD_XY = [(-60.4, -52.2), (-60.7, 52.2), (-59.1, 55.5), (52.0, 55.5), (52.2, 53.8), (69.7, 53.8),
           (75.3, 47.3), (76.8, 40.2), (76.8, -40.2), (75.3, -47.3), (69.7, -53.8), (52.2, -53.8),
           (52.0, -55.5), (-59.1, -55.5)]
# The snout is an arched hood (top plate sweeping down into thin side walls) round a
# goggle-shaped face panel set back at FACE_X. Half profiles (y >= 0, z) listed from the
# outside in, measured from the reference's height maps and mirrored.
SNOUT_X = 52.0                   # where the snout meets the front face of the main head
FACE_X = 60.0
HOOD_OUTER = [(53.7, 152.3), (53.5, 154.5), (51.5, 162.6), (49.5, 170.2), (47.5, 176.7), (45.5, 180.5),
              (43.5, 181.9), (41.5, 182.6), (39.5, 182.9)]
HOOD_INNER = [(50.6, 140.0), (50.6, 152.5), (49.5, 160.8), (47.5, 168.6), (45.5, 175.2), (43.5, 179.1),
              (41.5, 180.5)]
# Lower edge of the face panel: it reaches down into the two chin tabs and opens into a
# slot between the eyes, which widens under the hood's top plate.
GOGGLE = [(50.3, 153.0), (49.0, 152.2), (47.0, 151.3), (45.0, 150.5), (43.0, 149.9), (40.0, 149.75),
          (37.0, 149.9), (35.0, 150.2), (33.0, 150.6), (31.0, 151.2), (29.0, 151.8), (27.0, 152.6),
          (25.0, 153.5), (23.0, 154.5), (21.0, 155.7), (19.0, 157.0), (17.0, 158.4), (15.0, 160.2),
          (13.0, 162.8), (11.0, 170.5), (9.0, 175.0), (8.5, 177.5), (12.0, 178.4), (16.5, 180.5)]
CHIN_Z = 149.5                   # lowest point of the chin tabs
CHIN_Y = 49.0                    # the tabs end inside the hood walls
CHIN_X0 = 50.6                   # the tabs start a little behind the snout
# Arched cut-out under the nose in the main head's front face, and the notch at its top.
NOSE_ARCH = [(16.5, 152.3), (15.0, 154.1), (13.0, 156.3), (11.0, 158.4), (9.0, 160.3), (7.0, 162.0),
             (5.0, 163.3), (3.0, 164.1), (0.0, 164.5)]
NOSE_ARCH_X = 42.0
TOP_NOTCH = [(19.0, 184.3), (25.5, 190.5)]
TOP_NOTCH_X = 42.0
PANEL_LINES_X = (-4.5, 34.7, 42.2)
TOP_BAND_X = (-4.0, 34.2)
# Paint regions on the head's sides, traced from the reference texture. BD-1's two sides
# are painted differently. Each entry: (name, colour, surface, outline (x, z)), where
# surface is "side" (the flat side face), "edge" (the bevel along the top edge) or
# "hood" (the curved hood wall). Earlier entries win where outlines touch.
PAINT = {
    -1: [  # BD-1's right side
        ("panel_dot", RED, "side", [(9.9, 172.9), (14.4, 172.9), (14.4, 174.8), (9.9, 175.7)]),
        ("panel", GREY, "side", [(1.5, 179.5), (26.1, 179.5), (27.7, 178.6), (27.7, 159.5), (22.7, 158.6),
                                 (17.6, 158.6), (16.0, 159.5), (8.2, 167.3), (1.5, 171.9)]),
        ("stripe", RED, "side", [(-49.8, 180.5), (-46.2, 188.2), (-15.1, 188.2), (-9.7, 185.2), (22.7, 186.0),
                                 (30.9, 185.1), (33.0, 185.9), (33.7, 183.3), (33.7, 181.4), (-4.3, 181.4),
                                 (-4.8, 182.3), (-10.5, 182.4), (-16.6, 177.6), (-18.6, 179.5), (-49.5, 178.6)]),
        ("front_block", RED, "side", [(35.1, 181.4), (35.4, 185.1), (50.6, 185.2), (51.0, 181.4), (42.8, 181.4),
                                      (41.8, 184.3), (41.3, 181.4)]),
        ("back_strip", RED, "side", [(-48.6, 157.6), (-46.4, 159.5), (-33.8, 159.5), (-35.7, 158.0), (-34.0, 156.7),
                                     (-47.0, 156.7)]),
        ("top_edge", GREY, "edge", [(-4.4, 186.3), (41.6, 186.3), (41.6, 188.4), (-4.4, 188.4)]),
        ("snout", RED, "hood", [(52.9, 176.6), (54.0, 180.7), (62.3, 180.7), (63.8, 177.5), (65.0, 177.2),
                                (63.9, 155.8), (53.4, 155.8)]),
    ],
    1: [  # BD-1's left side
        ("stripe", RED, "side", [(-35.4, 187.6), (-13.7, 188.2), (-11.1, 186.8), (-7.5, 181.3), (33.1, 181.4),
                                 (33.7, 182.3), (40.9, 182.4), (42.0, 180.5), (41.3, 178.6), (35.8, 178.6),
                                 (35.0, 179.5), (34.4, 178.6), (-20.9, 178.6), (-21.0, 180.4), (-22.4, 181.4),
                                 (-21.0, 182.2), (-22.5, 184.2), (-34.6, 184.3), (-34.3, 186.7)]),
        ("top_edge", GREY, "edge", [(-4.4, 182.4), (42.0, 183.2), (42.5, 187.6), (42.5, 188.4), (-4.4, 188.4)]),
    ],
}
PAINT_FACE_Y = {"side": HEAD_Y, "edge": 54.8}   # face the pocket is measured from
# BD-1's right eye is the larger one with a blue lens and a set-back lip (width, depth)
# inside its barrel; the left lens carries a small raised ring round a shallow cup
# (outer radius, inner radius, top, cup floor). Lens dome heights from the reference.
EYES = {
    "right": dict(y=-29.25, z=166.3, r=13.0, lens_r=8.6, front=76.2, dome=5.0, lip=(1.5, 2.0),
                  ring=RED, lens=BLUE),
    "left": dict(y=26.5, z=166.3, r=10.4, lens_r=8.4, front=76.3, dome=4.0, lip=None,
                 nub=(3.2, 2.4, 77.8, 76.0), ring=GREY, lens=LENS_GREY),
}
EYE_BACK = 54.0           # floor of the eye sockets, 6 mm behind the face panel
RING_FRONT = 72.0
EAR = dict(x=-28.3, z=171.0, r=16.4, y0=HEAD_Y, y1=62.85)
# Ear relief as (radius, distance from the centre plane), fitted round the rim's centre:
# an outer ring with a flat rim and bevelled edge, and the grey centre that sits inside
# it against the head (red-painted cone, deep annular groove, hub, dimple).
EAR_RING = [(11.0, 55.5), (11.0, 62.85), (12.1, 62.85), (12.1, 62.45), (12.7, 62.45), (12.7, 62.85),
            (14.2, 62.85), (16.4, 56.3), (16.4, 55.5)]   # with a 0.6 mm groove for the red line
EAR_CENTRE = [(0.0, 55.5), (0.0, 59.8), (3.2, 59.8), (3.3, 61.6), (5.8, 61.9), (5.9, 55.9), (7.7, 55.9),
              (10.8, 62.4), (10.8, 55.5)]
# Antenna line fitted to the reference: it lies in the plane |y| = ANTENNA_Y and leaves
# the ear through a tapered collar (radius at the ear, radius at the end, length).
ANTENNA_BASE = (-36.09, 183.0)
ANTENNA_TIP = (-77.58, 242.79)
ANTENNA_Y = 59.48
ANTENNA_D = 2.1
ANTENNA_COLLAR = (1.96, 1.61, 7.0)
ANTENNA_SOCKET = 3.0      # how far the antenna goes in behind ANTENNA_BASE (stays clear of the ear centre)
# Green light panel recessed into the sloped back face, measured along the slope from
# the bottom edge; its face sits LIGHT_RECESS below the surface.
LIGHT_RECESS = 3.0
# Outline at the surface and at the floor (along-slope range, half width): the bottom
# edge is sharp, the top and side edges slope in over about 4 mm.
LIGHT_FACE = dict(along=(3.4, 36.7), y=52.0)
LIGHT_FLOOR = dict(along=(4.5, 32.5), y=48.5)


def _slope_frame():
    (xb, zb), (xt, zt) = HEAD_SIDE[0], HEAD_SIDE[3]
    L = math.hypot(xt - xb, zt - zb)
    u = ((xt - xb) / L, (zt - zb) / L)          # up the slope
    n = (-u[1], u[0])                            # outward (back and up)
    return (xb, zb), u, n


def slope_rect(outline, d, gap=0.0):
    """Closed wire of a rectangle lying parallel to the back slope, d below its surface."""
    (xb, zb), u, n = _slope_frame()
    (a0, a1), hw = outline["along"], outline["y"] - gap
    a0, a1 = a0 + gap, a1 - gap
    pts = []
    for a, y in ((a0, -hw), (a1, -hw), (a1, hw), (a0, hw)):
        pts.append(V(s(xb + u[0] * a + n[0] * d), s(y), s(zb + u[1] * a + n[1] * d)))
    return Part.makePolygon(pts + [pts[0]])


def light_pocket():
    """Recess with sloped top and side edges, lofted from the surface outline to the floor,
    plus room under the floor for the green insert."""
    floor_d = -LIGHT_RECESS
    taper = Part.makeLoft([slope_rect(LIGHT_FACE, 0.0), slope_rect(LIGHT_FLOOR, floor_d)], True, True)
    above = Part.makeLoft([slope_rect(LIGHT_FACE, 3.0), slope_rect(LIGHT_FACE, -0.01)], True, True)
    under = Part.makeLoft([slope_rect(LIGHT_FLOOR, floor_d + 0.01), slope_rect(LIGHT_FLOOR, floor_d - INLAY)], True, True)
    return taper.fuse([above, under])


def light_panel():
    """Green insert lining the floor of the back recess."""
    floor_d = -LIGHT_RECESS
    return Part.makeLoft([slope_rect(LIGHT_FLOOR, floor_d, g()), slope_rect(LIGHT_FLOOR, floor_d - INLAY, g())],
                         True, True)


def top_band_region(gap):
    x0, x1 = TOP_BAND_X
    return box(x0 + gap, x1 - gap, -HEAD_Y + 1.5 + gap, HEAD_Y - 1.5 - gap, HEAD_Z1 - INLAY, HEAD_Z1 + 3)


def side_region(poly, side, gap, y_face=HEAD_Y):
    p = offset_poly(poly, -gap)
    y_in = side * (y_face - INLAY)
    y_out = side * (y_face + 3)
    return prism_xz(p, min(y_in, y_out), max(y_in, y_out))


def eye_hole(e, gap):
    return cyl_x(e["y"], e["z"], e["r"] + gap, EYE_BACK, 90)


def neck_body(gap):
    """Square neck rod between the torso top and the head underside."""
    (x0, z0), (x1, z1) = NECK_AXIS
    L = math.hypot(x1 - x0, z1 - z0)
    ux, uz = (x1 - x0) / L, (z1 - z0) / L
    nx, nz = -uz, ux
    h = NECK_T / 2 + gap
    pts = [(x0 + nx * h, z0 + nz * h), (x1 + nx * h, z1 + nz * h),
           (x1 - nx * h, z1 - nz * h), (x0 - nx * h, z0 - nz * h)]
    return prism_xz(pts, -NECK_W / 2 - gap, NECK_W / 2 + gap)


def prism_xy(pts, z0, z1):
    """Polygon in the XY plane, extruded from z0 to z1."""
    w = Part.makePolygon([V(s(x), s(y), s(z0)) for x, y in pts] + [V(s(pts[0][0]), s(pts[0][1]), s(z0))])
    return Part.Face(w).extrude(V(0, 0, s(z1 - z0)))


def mirrored(half):
    """Left-to-right outline from a half profile listed from the outside in (y >= 0)."""
    left = [(-y, z) for y, z in half]
    right = [(y, z) for y, z in reversed(half)]
    return left + (right[1:] if half[-1][0] == 0 else right)


def closed_below(half, z_low):
    """Region under (or inside) a mirrored profile, closed off at z_low."""
    return [(-half[0][0], z_low)] + mirrored(half) + [(half[0][0], z_low)]


def head_solid():
    """Main head from the traced outlines, plus the arched hood and the goggle-shaped face panel."""
    outlines = prism_xz(HEAD_XZ, -60, 60).common(prism_xy(HEAD_XY, 140, 200))
    main = outlines.common(prism_yz(HEAD_YZ, -70, 90)).common(box(-70, SNOUT_X, -60, 60, 140, 200))
    snout = outlines.common(prism_yz(closed_below(HOOD_OUTER, 140.0), SNOUT_X - 0.01, 90))
    chin = box(CHIN_X0, FACE_X, -CHIN_Y, CHIN_Y, CHIN_Z, 153.0)
    h = main.fuse([snout, chin])
    cavity = prism_yz(closed_below(HOOD_INNER, 130.0), FACE_X, 90)
    below = prism_yz(closed_below(GOGGLE, 130.0), SNOUT_X, 90)
    # Shape the part of the tabs behind the snout the same way, below the main head only.
    below = below.fuse(prism_yz(closed_below(GOGGLE, 130.0), CHIN_X0 - 0.01, SNOUT_X + 0.01)
                       .common(box(CHIN_X0 - 1, SNOUT_X + 1, -60, 60, 130, HEAD_Z0)))
    arch = prism_yz(closed_below(NOSE_ARCH, 130.0), NOSE_ARCH_X, SNOUT_X + 0.5)
    (y0, z0), (y1, z1) = TOP_NOTCH
    notch = prism_yz([(-y0, z0), (y0, z0), (y1, z1), (y1, 200.0), (-y1, 200.0), (-y1, z1)],
                     TOP_NOTCH_X, SNOUT_X + 0.5)
    return h.cut([cavity, below, arch, notch]).removeSplitter()


def hood_region(poly, side, gap):
    """1 mm skin of the curved hood wall inside an (x, z) outline, on one side."""
    from shapely.geometry import Polygon
    outer = closed_below(HOOD_OUTER, 140.0)
    inner = Polygon(outer).buffer(-INLAY, join_style=2)
    skin = prism_yz(outer, 40, 90).cut(prism_yz(list(inner.exterior.coords)[:-1], 39, 91))
    return skin.common(prism_xz(offset_poly(poly, -gap), *ys(side, (0.0, 60.0))))


def paint_region(surface, poly, side, gap):
    if surface == "hood":
        return hood_region(poly, side, gap)
    return side_region(poly, side, gap, PAINT_FACE_Y[surface])


def paint_inlays(side):
    """(name, colour, solid) for each painted inlay on one side; later ones avoid earlier ones."""
    hs = head_solid()
    out, taken = [], []
    for name, colour, surface, poly in PAINT[side]:
        part = hs.common(paint_region(surface, poly, side, g()))
        if taken:
            part = part.cut(taken)
        taken.append(paint_region(surface, poly, side, 0))
        out.append((name, colour, part))
    return out


def head_shell():
    h = head_solid()
    # Panel lines: thin grooves running round the main box.
    for x in PANEL_LINES_X:
        ring = box(x - 0.4, x + 0.4, -HEAD_Y - 1, HEAD_Y + 1, HEAD_Z0 - 1, HEAD_Z1 + 1)
        ring = ring.cut(box(x - 1, x + 1, -HEAD_Y + 0.6, HEAD_Y - 0.6, HEAD_Z0 + 0.6, HEAD_Z1 - 0.6))
        h = h.cut(ring)
    cuts = [top_band_region(0), light_pocket()]
    for side in (1, -1):
        cuts += [paint_region(surface, poly, side, 0) for _, _, surface, poly in PAINT[side]]
        # 3 mm peg hole for the ear disc.
        cuts.append(pin_hole_y(EAR["x"], EAR["z"], side * (HEAD_Y - 8), side * HEAD_Y))
    for e in EYES.values():
        cuts.append(eye_hole(e, g()))
    cuts.append(neck_body(g()))
    return h.cut(cuts)


def eye_ring(e):
    """Eye barrel: seated 6 mm in the face panel, standing out to RING_FRONT, with a set-back inner lip."""
    outer = cyl_x(e["y"], e["z"], e["r"], EYE_BACK, RING_FRONT)
    cuts = [cyl_x(e["y"], e["z"], e["lens_r"] + g(), EYE_BACK - 1, RING_FRONT + 1)]
    if e["lip"]:
        lip_w, lip_d = e["lip"]
        cuts.append(cyl_x(e["y"], e["z"], e["lens_r"] + g() + lip_w, RING_FRONT - lip_d, RING_FRONT + 1))
    return outer.cut(cuts)


def lens(e):
    r, dome_h = e["lens_r"], e["dome"]
    body = cyl_x(e["y"], e["z"], r, EYE_BACK, e["front"] - dome_h)
    sph_r = (r * r + dome_h * dome_h) / (2 * dome_h)
    sph = Part.makeSphere(s(sph_r), V(s(e["front"] - sph_r), s(e["y"]), s(e["z"])))
    cap = sph.common(cyl_x(e["y"], e["z"], r, e["front"] - dome_h, e["front"] + 1))
    lens_solid = body.fuse(cap).removeSplitter()
    if "nub" in e:
        r_out, r_in, top, cup = e["nub"]
        ring = cyl_x(e["y"], e["z"], r_out, e["front"] - 1.5, top)
        lens_solid = lens_solid.fuse(ring).cut(cyl_x(e["y"], e["z"], r_in, cup, top + 1)).removeSplitter()
    return lens_solid


def revolve_y(profile, cx, cz, side):
    """Solid of revolution of a (radius, distance) profile about the Y-parallel axis through (cx, cz)."""
    pts = [V(s(cx + r), s(side * yv), s(cz)) for r, yv in profile]
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return face.revolve(V(s(cx), 0, s(cz)), V(0, 1, 0), 360)


def revolve_ear(profile, side):
    return revolve_y(profile, EAR["x"], EAR["z"], side)


def ear_disc(side):
    """Outer ear ring with its flat rim and bevelled edge; holds the antenna."""
    d = revolve_ear(EAR_RING, side)
    # Socket for the antenna rod, drilled along the antenna direction.
    (bx, bz), (tx, tz) = ANTENNA_BASE, ANTENNA_TIP
    L = math.hypot(tx - bx, tz - bz)
    dirv = V((tx - bx) / L, 0, (tz - bz) / L)
    yc = side * ANTENNA_Y
    start = V(s(bx), s(yc), s(bz)) - dirv * s(ANTENNA_SOCKET + 0.5)
    return d.cut(Part.makeCylinder(ROD_HOLE / 2, s(ANTENNA_SOCKET + 6), start, dirv)).removeSplitter()


def ear_centre(side):
    """Grey centre of the ear: cone (paint it red), deep annular groove, hub and dimple; pegs into the head."""
    c = revolve_ear([(min(r, 11.0 - g()), yv) for r, yv in EAR_CENTRE], side)
    peg = Part.makeCylinder(PIN_D / 2, s(6), V(s(EAR["x"]), s(side * EAR["y0"]), s(EAR["z"])), V(0, -side, 0))
    return c.fuse(peg).removeSplitter()


def antenna_exit():
    """Where the antenna line leaves the ear disc rim, and how far that is from ANTENNA_BASE."""
    (bx, bz), (tx, tz) = ANTENNA_BASE, ANTENNA_TIP
    L = math.hypot(tx - bx, tz - bz)
    dx, dz = (tx - bx) / L, (tz - bz) / L
    ox, oz = bx - EAR["x"], bz - EAR["z"]
    b = ox * dx + oz * dz
    t = -b + math.sqrt(b * b - (ox * ox + oz * oz - EAR["r"] ** 2))
    return (bx + dx * t, bz + dz * t), t


def antenna(side):
    """Printable antenna; a 2 mm brass rod of the same length is sturdier."""
    (bx, bz), (tx, tz) = ANTENNA_BASE, ANTENNA_TIP
    L = math.hypot(tx - bx, tz - bz)
    dirv = V((tx - bx) / L, 0, (tz - bz) / L)
    yc = side * ANTENNA_Y
    start = V(s(bx), s(yc), s(bz)) - dirv * s(ANTENNA_SOCKET)
    rod = Part.makeCylinder(min(s(ANTENNA_D / 2), ROD_HOLE / 2 - 0.1), s(L + ANTENNA_SOCKET), start, dirv)
    (ex, ez), _ = antenna_exit()
    r0, r1, length = ANTENNA_COLLAR
    collar = Part.makeCone(s(r0), s(r1), s(length), V(s(ex), s(yc), s(ez)), dirv)
    tip = Part.makeCone(s(ANTENNA_D / 2), 0.2, s(3), V(s(tx), s(yc), s(tz)), dirv)
    return rod.fuse([collar, tip]).removeSplitter()


# ---------------------------------------------------------------- body
TORSO = dict(x0=-17.8, x1=36.2, y=25.3, z0=86.0, z1=131.9)
TORSO_XZ = [(-17.7, 86.3), (-17.8, 128.3), (-8.2, 131.9), (28.2, 131.9), (29.6, 131.4), (36.2, 123.5),
            (36.0, 91.0), (23.9, 87.5), (16.0, 86.1), (-16.7, 86.0)]
TORSO_YZ = [(-25.3, 93.6), (-25.3, 122.4), (-25.2, 128.3), (-17.1, 131.9), (17.1, 131.9),
            (25.2, 128.3), (25.3, 122.4), (25.3, 93.6), (25.0, 86.2),
            (-25.0, 86.2), (-25.3, 93.6)]
# Plan outline: sides taper towards the front and step out round the hip.
TORSO_XY = [(-17.8, -24.8), (-17.8, 24.8), (-11.3, 25.3), (17.4, 25.3),
            (21.5, 24.8), (27.0, 23.8), (32.1, 22.8), (35.6, 21.8), (36.3, 21.0),
            (36.3, -21.0), (35.6, -21.8), (32.1, -22.8), (27.0, -23.8), (21.5, -24.8),
            (17.4, -25.3), (-11.3, -25.3)]
# Round recess in each side of the torso round the hip joint (x, z), and its floor.
HIP_RECESS_XZ = [(-10.5, 105.5), (-10.5, 110.5), (-8.5, 115.5), (-4.5, 119.5), (0.5, 121.5), (6.0, 121.5),
                 (10.0, 120.0), (14.0, 116.5), (16.5, 111.0), (16.5, 105.0), (14.0, 99.5), (10.0, 96.0),
                 (5.5, 94.5), (0.5, 94.5), (-4.5, 96.5), (-8.5, 100.5)]
HIP_RECESS_FLOOR = 21.0
HIP_RECESS_LIP = (0.75, 26.65)      # raised lip round the recess: width, top
# The edges between the top face and the sides are bevelled, more towards the front:
# a plane |y| = a + b x + c z fitted to the reference, applied for x >= x0.
TORSO_CORNER_BEVEL = dict(a=154.741, b=-0.3602, c=-0.9695, x0=19.0)
CHEST_DEPTH = 5.2                    # the grey chest plate sits this far behind the front face
# Recessed back panel: outline at the back face and at its floor (y half-width, z0, z1, x).
BACK_PANEL = dict(face=(22.5, 89.5, 125.0, -17.8), floor=(20.5, 92.0, 122.0, -13.9))
NECK_AXIS = ((29.6, 121.9), (1.1, 158.8))
NECK_T, NECK_W = 9.3, 9.4
CHEST_PLATE = [(-13.5, 120.5), (13.5, 120.5), (13.5, 105.0), (11.0, 103.0), (11.0, 94.8), (-11.0, 94.8),
               (-11.0, 103.0), (-13.5, 105.0)]   # (y, z), stepped in near the bottom
CHEST_TAB_HW = 5.0                   # half width of the red tab on the top chamfer
HIP = (5.0, 110.5)


def torso_solid():
    """Intersection of the traced side, front and plan outlines, with the top side edges bevelled."""
    t = (prism_xz(TORSO_XZ, -30, 30).common(prism_yz(TORSO_YZ, -25, 45))
         .common(prism_xy(TORSO_XY, 80, 140)))
    b = TORSO_CORNER_BEVEL
    cuts = []
    for side in (1, -1):
        corners = [(b["x0"], 118.0), (45.0, 118.0), (45.0, 140.0), (b["x0"], 140.0)]
        vs = [V(s(x), s(side * (b["a"] + b["b"] * x + b["c"] * zz)), s(zz)) for x, zz in corners]
        face = Part.Face(Part.makePolygon(vs + [vs[0]]))
        cuts.append(face.extrude(V(0, s(side * 30), 0)))
    return t.cut(cuts)


def chest_floor_x():
    return TORSO["x1"] - CHEST_DEPTH - INLAY


def chest_plate_region(gap):
    return prism_yz(offset_poly(CHEST_PLATE, -gap), chest_floor_x(), TORSO["x1"] + 3)


def back_panel_recess():
    """Recess in the torso's back with sloped edges, lofted from the face outline to the floor."""
    def rect(hw, z0, z1, x):
        pts = [V(s(x), s(-hw), s(z0)), V(s(x), s(hw), s(z0)), V(s(x), s(hw), s(z1)), V(s(x), s(-hw), s(z1))]
        return Part.makePolygon(pts + [pts[0]])
    hw, z0, z1, x = BACK_PANEL["face"]
    loft = Part.makeLoft([rect(*BACK_PANEL["face"]), rect(*BACK_PANEL["floor"])], True)
    return loft.fuse(box(x - 3, x + 0.01, -hw, hw, z0, z1))


def torso():
    t = torso_solid()
    lip_w, lip_top = HIP_RECESS_LIP
    # Under the thigh's rim the lip is lowered just enough to clear it.
    under_thigh = offset_poly(THIGH_XZ, g())
    clear = THIGH_Y[0] - GLUE_GAP / K
    lip_ring = [outer_slab(side, offset_poly(HIP_RECESS_XZ, lip_w), TORSO["y"] - 0.01, lip_top)
                .cut(outer_slab(side, under_thigh, clear, lip_top + 1)) for side in (1, -1)]
    t = t.fuse(lip_ring)
    recesses = [outer_slab(side, HIP_RECESS_XZ, HIP_RECESS_FLOOR, lip_top + 1) for side in (1, -1)]
    t = t.cut([chest_plate_region(0), back_panel_recess(), neck_body(g()),
               pin_hole_y(HIP[0], HIP[1], -TORSO["y"], TORSO["y"])] + recesses)
    # Red tab: a pocket 1 mm deep into the top chamfer.
    return t.cut(_chamfer_pocket(0))


def _chamfer_pocket(gap):
    """Pocket for the red tab, 1 mm deep, normal to the torso's top front chamfer."""
    hw = CHEST_TAB_HW
    a, b = TORSO_XZ[4], TORSO_XZ[5]           # chamfer from the top face down to the front face
    c = math.hypot(b[0] - a[0], b[1] - a[1])
    n = ((a[1] - b[1]) / c, (b[0] - a[0]) / c)  # outward: forward and up
    t0, t1 = 0.15 + gap / c, 0.85 - gap / c
    p0 = along(a, b, t0)
    p1 = along(a, b, t1)
    pts = [(p0[0] - n[0] * INLAY, p0[1] - n[1] * INLAY), (p1[0] - n[0] * INLAY, p1[1] - n[1] * INLAY),
           (p1[0] + n[0] * 3, p1[1] + n[1] * 3), (p0[0] + n[0] * 3, p0[1] + n[1] * 3)]
    return prism_xz(pts, -hw + gap, hw - gap)


def chest_plate():
    """Grey plate lining the floor of the chest recess, with two screw dimples."""
    x0 = chest_floor_x()
    p = prism_yz(offset_poly(CHEST_PLATE, -g()), x0, x0 + INLAY)
    for y in (-6.0, 6.0):
        p = p.cut(cyl_x(y, 113.0, 1.2, x0 + INLAY - 0.5, x0 + INLAY + 1))
    return p


def chest_tab():
    return torso_solid().common(_chamfer_pocket(g()))


def neck():
    n = neck_body(0)
    # Trim the ends so they stop inside the sockets (8 mm deep each side).
    return n.common(box(-50, 80, -10, 10, TORSO["z1"] - 8, HEAD_Z0 + 8))


# ---------------------------------------------------------------- legs
KNEE = (-17.5, 72.0)          # centre of the knee bolt on the reference
ANKLE = (39.3, 9.8)
THIGH_Y = (26.36, 32.6)          # inner rim and outer face of the thigh plate
# The plate is a shallow tray: hollow underneath down to THIGH_HOLLOW, inside a rim
# THIGH_RIM wide. A hub hidden in the torso's hip recess carries the hip pin.
THIGH_HOLLOW = 28.24
THIGH_RIM = 2.5
HIP_HUB_R = 5.5
SHIN_Y = (19.2, 25.9)
SHIN_PLATE_Y = (28.6, 31.5)      # red shin plate face, and its two lugs
# Side outlines (x, z) traced from the reference mesh with ref_profiles.py.
THIGH_XZ = [(-27.9, 73.3), (-26.6, 77.1), (-23.9, 80.2), (-20.7, 81.5), (-18.1, 85.7), (-22.4, 94.8),
            (-9.4, 117.3), (-4.3, 121.5), (1.9, 123.3), (8.2, 122.7), (13.6, 119.5), (17.3, 114.4),
            (18.3, 111.4), (18.5, 104.9), (17.7, 101.6), (4.7, 79.1), (-5.4, 78.3), (-7.7, 74.0),
            (-7.3, 70.5), (-8.6, 66.7), (-11.2, 63.6), (-14.9, 61.9), (-18.9, 61.6), (-22.8, 62.9),
            (-25.8, 65.6), (-27.6, 69.2)]
SHIN_XZ = [(-28.1, 73.2), (-27.0, 76.9), (-24.6, 79.8), (-21.3, 81.7), (-17.5, 82.1), (-13.9, 81.0),
           (-10.9, 78.6), (40.9, 16.9), (42.5, 14.2), (43.1, 11.4), (42.6, 8.7), (41.2, 6.7), (38.9, 5.6),
           (36.2, 5.6), (31.1, 8.7), (0.4, 45.3), (-6.7, 47.7), (-19.2, 62.7), (-22.9, 63.7),
           (-25.8, 66.1), (-27.7, 69.5)]
# Thigh greebles, traced from the reference's outer-face height map (x, z).
CHANNEL_XZ = [(-15.0, 82.0), (-13.5, 92.0), (-1.0, 113.5), (4.0, 118.5), (7.0, 120.0), (10.5, 118.5),
              (11.5, 117.5), (11.5, 111.0), (10.5, 108.0), (-2.5, 85.0), (-7.4, 81.9), (-9.0, 79.5),
              (-11.0, 79.0)]
CHANNEL_FLOOR = 31.1             # visible floor of the red channel (top of the red insert)
# Patch of the channel floor that rises nearly flush, to CHANNEL_RAISED_FACE (traced).
CHANNEL_RAISED_XZ = [(-6.2, 104.0), (0.5, 114.6), (10.2, 108.9), (4.0, 97.5), (-1.2, 101.5), (-6.0, 103.0)]
CHANNEL_RAISED_FACE = 32.4
HEX_SOCKET = dict(x=1.5, z=105.6, r=3.0)   # hex recess in the upper channel, down to CHANNEL_FLOOR
# Rod, shank and threaded cylinder fitted to the reference (axis ends, radius, top).
ROD = dict(start=(-11.81, 81.41), end=(-3.85, 95.20), r=1.28, top=34.76)    # threaded part
SHANK = dict(start=(-3.85, 95.20), end=(-0.58, 100.89), r=2.35, top=35.62)  # plain bolt shank under the hex
SLOT_XZ = [(1.5, 87.0), (10.5, 104.0), (14.5, 102.0), (5.5, 85.0)]
SLOT_DEPTH = 1.5
PISTON = dict(start=(3.61, 85.60), end=(12.74, 103.22), r=2.2, top=33.2, cap_r=2.27, cap_top=33.76, cap_len=6.9)
# Knee bolt as (radius, distance from the centre plane): bevelled base, ring, a narrow
# groove, the boss, and a round socket in the middle (the star on the reference is only
# texture). It sits in a pocket that leaves a visible groove round it.
KNEE_CAP = dict(profile=[(9.2, 32.6), (7.5, 34.6), (7.4, 34.79), (5.5, 34.79), (5.5, 33.6), (4.9, 33.6),
                         (4.9, 35.16), (2.9, 35.16), (2.9, 33.6), (0.0, 33.6)],
                pocket_r=9.9, sink=1.5)
THIGH_BEVEL = 1.25               # the outer face is this much smaller than the outline all round
# Red shin plate and its two lugs, traced the same way.
SHIN_PLATE_XZ = [(-10.5, 59.5), (-9.3, 59.0), (-8.2, 59.0), (-3.0, 64.0), (-1.5, 64.5), (31.0, 26.5),
                 (28.2, 28.0), (22.0, 22.0), (2.0, 45.0), (-1.0, 48.5), (-4.0, 52.0)]
SHIN_LUGS_XZ = [[(-13.0, 63.0), (-6.5, 69.5), (-2.0, 65.0), (-2.0, 64.0), (-8.5, 58.5)],
                [(22.5, 21.5), (22.5, 23.0), (28.5, 28.5), (33.0, 24.0), (33.0, 23.0), (26.5, 17.5)]]
FOOT_Y = (17.9, 27.2)
# Foot plate side profile (x, z) and its two through-slots, measured from the reference.
FOOT_SIDE = [(9.5, 0.0), (56.6, 0.0), (56.6, 3.1), (54.8, 4.1), (50.0, 5.2), (31.0, 5.3), (25.0, 4.1),
             (20.0, 2.3), (17.5, 1.7), (13.0, 1.7), (11.5, 1.2), (9.5, 0.1)]
FOOT_SLOTS = dict(x=((31.3, 36.5), (46.3, 48.9)), y=(19.6, 24.6), floor=0.4)   # slots keep a thin floor
# Ankle fork: two side plates round the end of the shin, joined by a low cross block.
FORK_Y = ((16.6, 19.0), (26.1, 28.2))
FORK_XZ = [(36.5, 0.0), (46.0, 0.0), (46.0, 5.9), (41.2, 13.0), (39.8, 13.2), (36.5, 12.0)]
FORK_BLOCK = dict(x=(37.5, 45.5), z=(0.0, 5.4))


def ys(side, pair):
    a, b = side * pair[0], side * pair[1]
    return min(a, b), max(a, b)


def offset_poly(pts, d):
    """Grow (d > 0) or shrink (d < 0) a 2D outline with mitred corners; returns its largest piece."""
    from shapely.geometry import Polygon
    p = Polygon(pts).buffer(d, join_style=2)
    if p.geom_type == "MultiPolygon":
        p = max(p.geoms, key=lambda q: q.area)
    return [(x, z) for x, z in list(p.exterior.coords)[:-1]]


def union_poly(polys):
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    u = unary_union([Polygon(p) for p in polys]).buffer(0.01, join_style=2)
    return [(x, z) for x, z in list(u.exterior.coords)[:-1]]


def outer_slab(side, pts, y_from, y_to):
    """Prism of an (x, z) outline between two distances from the centre plane, on one side."""
    return prism_xz(pts, *ys(side, (y_from, y_to)))


def offset_matched(pts, d):
    """offset_poly with the same vertex count, order and start as pts (for lofting), or None."""
    out = offset_poly(pts, d)
    if len(out) != len(pts):
        return None
    k = min(range(len(out)), key=lambda i: math.hypot(out[i][0] - pts[0][0], out[i][1] - pts[0][1]))
    out = out[k:] + out[:k]
    fwd = math.hypot(out[1][0] - pts[1][0], out[1][1] - pts[1][1])
    back = math.hypot(out[-1][0] - pts[1][0], out[-1][1] - pts[1][1])
    if fwd > back:
        out = [out[0]] + out[1:][::-1]
    return out


def xz_wire(pts, y):
    vs = [V(s(x), s(y), s(z)) for x, z in pts]
    return Part.makePolygon(vs + [vs[0]])


def thigh_solid(side):
    """Thigh plate: a thin full-outline base, then a steep bevel lofted up to the smaller outer face."""
    y0, y1 = THIGH_Y
    base_top = y0 + 0.1
    face = offset_matched(THIGH_XZ, -THIGH_BEVEL)
    base = outer_slab(side, THIGH_XZ, y0, base_top)
    if face is None:
        return base.fuse(outer_slab(side, THIGH_XZ, base_top - 0.01, y1))
    loft = Part.makeLoft([xz_wire(THIGH_XZ, side * base_top), xz_wire(face, side * y1)], True, True)
    tray = base.fuse(loft).removeSplitter().cut(outer_slab(side, offset_poly(THIGH_XZ, -THIGH_RIM), y0 - 1, THIGH_HOLLOW))
    hub = cyl_y(HIP[0], HIP[1], HIP_HUB_R, side * (HIP_RECESS_FLOOR + 0.3), side * (THIGH_HOLLOW + 0.1))
    return tray.fuse(hub).removeSplitter()


def thigh(side):
    t = thigh_solid(side)
    insert_floor = CHANNEL_FLOOR - INLAY
    t = t.cut([outer_slab(side, CHANNEL_XZ, insert_floor, THIGH_Y[1] + 3),
               outer_slab(side, SLOT_XZ, THIGH_Y[1] - SLOT_DEPTH, THIGH_Y[1] + 3),
               cyl_y(KNEE[0], KNEE[1], KNEE_CAP["pocket_r"], side * (THIGH_Y[1] - KNEE_CAP["sink"]),
                     side * (THIGH_Y[1] + 3))])
    y0, y1 = ys(side, (HIP_RECESS_FLOOR, THIGH_Y[1]))
    for x, z in (HIP, KNEE):
        t = t.cut(pin_hole_y(x, z, y0, y1))
    return t


def thigh_channel(side):
    """Insert lining the thigh channel: low floor round the rod, nearly flush patch above, with a hex recess."""
    inner = offset_poly(CHANNEL_XZ, -g())
    floor = outer_slab(side, inner, CHANNEL_FLOOR - INLAY, CHANNEL_FLOOR)
    face = CHANNEL_RAISED_FACE
    upper = outer_slab(side, offset_poly(CHANNEL_RAISED_XZ, -g()), CHANNEL_FLOOR - 0.01, face).common(
        outer_slab(side, inner, CHANNEL_FLOOR - 1, face + 1))
    hs = HEX_SOCKET
    hexagon = Part.makePolygon([V(s(hs["x"] + hs["r"] * math.cos(math.pi / 3 * i)), s(side * CHANNEL_FLOOR),
                                  s(hs["z"] + hs["r"] * math.sin(math.pi / 3 * i))) for i in range(7)])
    socket = Part.Face(hexagon).extrude(V(0, s(side * (face - CHANNEL_FLOOR + 1)), 0))
    # Clearance for the bolt shank where it runs up into the raised part.
    from shapely.geometry import LineString
    shank = LineString([SHANK["start"], SHANK["end"]]).buffer(SHANK["r"] + g())
    notch = outer_slab(side, list(shank.exterior.coords)[:-1], CHANNEL_FLOOR, face + 1)
    return floor.fuse(upper).removeSplitter().cut([socket, notch])


def thigh_channel_parts(side):
    """The channel insert split by colour: red raised patch, dark floor round the rod, dark top tip."""
    whole = thigh_channel(side)
    tall = (CHANNEL_FLOOR - INLAY - 1, CHANNEL_RAISED_FACE + 1)
    red = whole.common(outer_slab(side, offset_poly(CHANNEL_RAISED_XZ, -g() / 2), *tall))
    dark = whole.cut(outer_slab(side, offset_poly(CHANNEL_RAISED_XZ, g() / 2), *tall))
    floor, tip = sorted(dark.Solids, key=lambda so: -so.Volume)[:2]
    return red, floor, tip


def _threaded(start, end, r, y_axis, side, ridges, ridge=0.35):
    """Cylinder along an (x, z) segment at height y_axis, with a few thread ridges."""
    (x0, z0), (x1, z1) = start, end
    L = math.hypot(x1 - x0, z1 - z0)
    d = V((x1 - x0) / L, 0, (z1 - z0) / L)
    origin = V(s(x0), s(side * y_axis), s(z0))
    c = Part.makeCylinder(s(r), s(L), origin, d)
    for i in range(1, ridges + 1):
        c = c.fuse(Part.makeCylinder(s(r + ridge), s(0.8), origin + d * s(L * i / (ridges + 1.5)), d))
    return c, origin, d, L


def thigh_rod(side):
    """Grey threaded rod lying on the red channel floor, from the hex down to the knee."""
    y_rod = ROD["top"] - ROD["r"]
    rod, origin, d, L = _threaded(ROD["start"], ROD["end"], ROD["r"], y_rod, side, 6, ridge=0.3)
    rod = rod.fuse(Part.makeSphere(s(ROD["r"]), origin))
    y_sh = SHANK["top"] - SHANK["r"]
    shank, o2, d2, L2 = _threaded(SHANK["start"], SHANK["end"], SHANK["r"], y_sh, side, 0)
    shank = shank.fuse(Part.makeSphere(s(SHANK["r"]), o2 + d2 * s(L2)))
    # Webs under both so the part sits flat on the floor.
    webs = [capsule_xz(p["start"], p["r"] * 0.6, p["end"], p["r"] * 0.6, *ys(side, (CHANNEL_FLOOR, p["top"] - p["r"])))
            for p in (ROD, SHANK)]
    part = rod.fuse([shank] + webs).removeSplitter()
    return part.common(outer_slab(side, offset_poly(CHANNEL_XZ, -g()), CHANNEL_FLOOR, SHANK["top"] + 1))


def thigh_piston(side):
    """Grey threaded cylinder in the slot beside the channel, with a cap at its upper end."""
    floor = THIGH_Y[1] - SLOT_DEPTH
    y_axis = PISTON["top"] - PISTON["r"]
    p, origin, d, L = _threaded(PISTON["start"], PISTON["end"], PISTON["r"], y_axis, side, 4, ridge=0.25)
    # The cap is thicker and sits a little higher than the threaded body.
    lift = V(0, s(side * (PISTON["cap_top"] - PISTON["cap_r"] - y_axis)), 0)
    cap = Part.makeCylinder(s(PISTON["cap_r"]), s(PISTON["cap_len"]), origin + d * s(L - PISTON["cap_len"]) + lift, d)
    p = p.fuse(cap).removeSplitter()
    return p.common(outer_slab(side, offset_poly(SLOT_XZ, -g()), floor, PISTON["cap_top"]))


def knee_cap(side):
    """Grey knee bolt revolved from KNEE_CAP's profile."""
    kc = KNEE_CAP
    y_in = THIGH_Y[1] - kc["sink"]
    profile = [(0.0, y_in), (kc["profile"][0][0], y_in)] + kc["profile"]
    cap = revolve_y(profile, KNEE[0], KNEE[1], side)
    peg = Part.makeCylinder(PIN_D / 2, s(4), V(s(KNEE[0]), s(side * y_in), s(KNEE[1])), V(0, -side, 0))
    return cap.fuse(peg).removeSplitter()


def shin_plate_outline():
    return union_poly([SHIN_PLATE_XZ] + SHIN_LUGS_XZ)


def shin(side):
    y0, y1 = ys(side, SHIN_Y)
    sh = prism_xz(SHIN_XZ, y0, y1)
    # Spacer boss at the knee, reaching into the thigh's hollow so the shin bears on the plate.
    sh = sh.fuse(cyl_y(KNEE[0], KNEE[1], 6.0, side * SHIN_Y[1], side * (THIGH_HOLLOW - 0.2))).removeSplitter()
    sh = sh.cut(outer_slab(side, shin_plate_outline(), SHIN_Y[1] - INLAY, SHIN_Y[1] + 8))
    for x, z in (KNEE, ANKLE):
        sh = sh.cut(pin_hole_y(x, z, y0 - 2, y1 + 2))
    return sh


def shin_plate(side):
    """Red plate on the outside of the shin, seated in a 1 mm pocket, with two raised lugs."""
    base = outer_slab(side, offset_poly(shin_plate_outline(), -g()), SHIN_Y[1] - INLAY, SHIN_PLATE_Y[0])
    lugs = [outer_slab(side, offset_poly(l, -g()), SHIN_PLATE_Y[0] - 0.01, SHIN_PLATE_Y[1]) for l in SHIN_LUGS_XZ]
    p = base.fuse(lugs).removeSplitter()
    # Keep the upper lug clear of the thigh plate it tucks under.
    return p.cut(outer_slab(side, offset_poly(THIGH_XZ, 0.4), THIGH_Y[0] - 0.4, THIGH_Y[1] + 1))


def foot(side):
    """Foot plate with two slots, and the ankle fork that takes the shin's pin."""
    y0, y1 = ys(side, FOOT_Y)
    f = prism_xz(FOOT_SIDE, y0, y1)
    for x0, x1 in FOOT_SLOTS["x"]:
        f = f.cut(box(x0, x1, *ys(side, FOOT_SLOTS["y"]), FOOT_SLOTS["floor"], 10))
    fork = [prism_xz(FORK_XZ, *ys(side, pair)) for pair in FORK_Y]
    blk = FORK_BLOCK
    fork.append(box(*blk["x"], *ys(side, (FORK_Y[0][1] - 0.01, FORK_Y[1][0] + 0.01)), *blk["z"]))
    f = f.fuse(fork).removeSplitter()
    a, b = ys(side, (FORK_Y[0][0], FORK_Y[1][1]))
    return f.cut(pin_hole_y(ANKLE[0], ANKLE[1], a, b))


# ---------------------------------------------------------------- stand
# The figure's centre of mass sits about 1 mm in front of the heels, so it
# needs a base to stand reliably. Feet glue into 1.2 mm pockets.
STAND = dict(cx=10.0, rx=78.0, ry=48.0, z0=-4.0, z1=1.2)


def stand():
    st = STAND
    e = Part.Ellipse(V(s(st["cx"]), 0, s(st["z0"])), s(st["rx"]), s(st["ry"]))
    plate = Part.Face(Part.Wire(e.toShape())).extrude(V(0, 0, s(st["z1"] - st["z0"])))
    plate = try_fillet(plate, 1.0, [ed for ed in plate.Edges if abs(ed.BoundBox.ZMax - s(st["z1"])) < 1e-6])
    for side in (1, -1):
        y0, y1 = ys(side, (FORK_Y[0][0], FORK_Y[1][1]))
        pocket = box(FOOT_SIDE[0][0] - g(), FOOT_SIDE[1][0] + g(), y0 - g(), y1 + g(), 0, st["z1"] + 1)
        plate = plate.cut(pocket)
    return plate


# ---------------------------------------------------------------- assembly
def parts():
    """List of (name, shape, colour, note) for every printable part."""
    hs = head_solid()
    out = [
        ("head_shell", head_shell(), WHITE, "头壳（米白）；顶带、侧板、红条、绿灯、眼睛都是嵌件"),
        ("head_top_band", hs.common(top_band_region(g())), GREY, "头顶灰色横带"),
        ("head_light", light_panel(), GREEN, "头后斜面凹槽里的绿色灯板"),
    ]
    for side, tag in ((1, "left"), (-1, "right")):
        out += [(f"paint_{tag}_{name}", solid, colour, "头侧涂装嵌件（两侧图案不同）")
                for name, colour, solid in paint_inlays(side)]
    for tag, e in EYES.items():
        out += [
            (f"eye_ring_{tag}", eye_ring(e), e["ring"], f"{'右' if tag == 'right' else '左'}眼外圈"),
            (f"lens_{tag}", lens(e), e["lens"], f"{'右眼蓝色' if tag == 'right' else '左眼浅灰'}镜头"),
        ]
    for side, tag in ((1, "left"), (-1, "right")):
        out += [
            (f"ear_{tag}", ear_disc(side), WHITE, "耳盘外圈（细槽里涂红线）"),
            (f"ear_centre_{tag}", ear_centre(side), GREY, "耳盘中心灰件"),
            (f"antenna_{tag}", antenna(side), WHITE, "天线；可换 2 mm 黄铜棒"),
        ]
    out += [
        ("neck", neck(), WHITE, "斜向方颈，两端各插 8 mm"),
        ("torso", torso(), WHITE, "躯干；髋部 3 mm 通孔"),
        ("chest_plate", chest_plate(), GREY, "胸前灰板"),
        ("chest_tab", chest_tab(), RED, "胸口上沿红色小块"),
    ]
    for side, tag in ((1, "left"), (-1, "right")):
        out += [
            (f"thigh_{tag}", thigh(side), WHITE, "大腿板"),
            (f"thigh_channel_{tag}", thigh_channel_parts(side)[0], RED, "大腿槽上段的红色凸块"),
            (f"thigh_channel_floor_{tag}", thigh_channel_parts(side)[1], DARK, "大腿槽底（深色），螺杆粘在上面"),
            (f"thigh_channel_tip_{tag}", thigh_channel_parts(side)[2], DARK, "大腿槽顶端的深色小块"),
            (f"thigh_rod_{tag}", thigh_rod(side), GREY, "大腿红槽里的螺杆"),
            (f"thigh_piston_{tag}", thigh_piston(side), GREY, "大腿侧槽里的螺纹柱"),
            (f"knee_cap_{tag}", knee_cap(side), GREY, "膝盖螺栓盖"),
            (f"shin_{tag}", shin(side), WHITE, "小腿"),
            (f"shin_plate_{tag}", shin_plate(side), RED, "小腿外侧红板，带两个凸耳"),
            (f"foot_{tag}", foot(side), DARK, "脚"),
        ]
    out.append(("stand", stand(), DARK, "展示底座（可选）：重心离脚跟只有约 1 mm，建议把脚粘进底座的凹槽"))
    return out


def build_document(name="BD1"):
    doc = App.newDocument(name)
    for pname, shape, colour, note in parts():
        obj = doc.addObject("Part::Feature", pname)
        obj.Shape = shape
        obj.Label2 = note
        if App.GuiUp:
            obj.ViewObject.ShapeColor = colour
    doc.recompute()
    return doc
