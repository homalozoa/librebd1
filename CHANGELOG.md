# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- MIT license for the scripts, CC BY-NC-SA 4.0 for the model files, and a fan-work notice in the README.

### Removed

- `compare_sheet.png` is no longer tracked: it shows the reference's textures.

## [0.1.0] - 2026-10-30

First release: a modular, printable BD-1 measured from the reference mesh,
with the tools used to measure and compare it.

### Added

- Parametric FreeCAD model (`bd1_model.py`) of BD-1, split into 54 parts by
  colour and joined with 3 mm pins and glue; `BD1_HEIGHT` scales it while pin
  holes and glue gaps keep their real size.
- Head: arched hood round a goggle-shaped face panel, eye barrels and lenses,
  arched cut-out under the nose and notch at the top, recessed green light
  panel on the back slope, ears revolved from the measured profile, antennas
  with a separate tapered collar.
- Torso: traced side, front and plan outlines with bevelled top edges,
  recessed chest plate, red tab, recessed back panel, hip recesses with a
  raised lip.
- Legs: tray-shaped thigh plates with a two-tone channel, threaded rod and
  threaded cylinder, layered knee bolt, shins with a raised red plate and two
  lugs, two-tone feet with slots and an ankle fork, and a hip hub that carries
  the hip pin.
- Paint: per-side head markings traced from the reference texture, and a
  palette whose colours are area-weighted means of the texture.
- Display stand, needed because the centre of mass is behind the heels.
- Tools: `glb_ref.py` (skinned, textured reference loader), `ref_profiles.py`
  (outline tracing), `heightmap.py` (mesh rasteriser), `render_views.py`,
  `compare.py` (outline IoU and band deviations), `depth_diff.py` (six-way
  surface comparison), `check_fit.py`, `export_stl.py`, `preview_gui.py`.

### Fixed

- Ear centre refitted to (-28.3, 171.0); hood profile half-millimetre offset.
- Eye lens domes, left-eye barrel and lens ring, red band on the right barrel.
- Thigh edge bevel, knee centre and bolt profile, rod and cylinder axes.
- Torso plan taper, back corners, chest recess outline and chest tab position.
- Chin tabs, head underside corners, antenna line, light recess edges.

### Known differences from the reference

- Deliberate, for printing: the hip hub (the reference's thighs float), glue
  gaps and pin holes, 0.4 mm floors in the foot slots, and the stand.
- Not representable: sub-millimetre sculpted detail and texture-only
  weathering (dirt, scratches, gradients, colour spots under about 3 mm).
