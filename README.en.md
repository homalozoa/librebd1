# openbd1: a modular, printable BD-1 (FreeCAD)

[中文](README.md) · English

The shape is modelled from measurements of a reference mesh kept in `bd-1-droid-star-wars-jedi-fallen-order/`. The outlines of the head, torso, thighs, shins and neck were traced from that mesh. The finer details (the face hood, the ear discs, the chest and back recesses, the rods and threaded pistons on the thighs, the lugs on the red shin plates, the feet and the ankle forks) were measured from height maps of the mesh surface taken from six directions. Every colour region is its own part, so you can print in colour, or print everything white and paint the pieces afterwards. Parts join with 3 mm pins and glue.

![preview](preview.png)

Orthographic views compared with the reference mesh (the comparison sheet `compare_sheet.png` contains the reference's textures, so it is not published; generate it yourself with `compare.py`):

| View | Silhouette overlap (IoU) |
|---|---|
| Front | 0.976 |
| Side | 0.983 |
| Top | 0.994 |

Surface relief is compared point by point with `depth_diff.py` from front, back, left, right, top and bottom, at 0.5 mm per pixel. The remaining differences are all under 66 mm², average about 2 mm or less, and most are one-pixel strips along part edges. Colours are the area-weighted average of the reference texture over each surface (see the colour table below).

Main details:
- **Face**: the snout is an arched hood with grey blocks on its curved sides. The top plate is 2.5 mm thick, and the outer edges curve in to form thin side walls. The panel inside the hood sits 10–16 mm back, its lower edge shaped like goggles that reach down to two small chin tabs, with a vertical slot between the eyes running up to the top plate. The front of the main head has an arched cut-out under the nose and a trapezoid notch in the middle of the top.
- **Eyes**: the right eye barrel is dark oxblood with a 1.5 mm bright red ring on its face. Its lens is steel blue with a 5 mm domed top, and the barrel has a recessed inner rim. The left barrel is light grey with no inner rim, and the centre of its lens has a small raised ring around a shallow dimple.
- **Ears**: the outer ring has a flat rim with a 45° chamfer and a 0.6 mm groove on it for a red line. The grey centre piece runs from a cone to a deep ring groove, a raised hub and a small centre dimple. The antenna follows a line fitted to the reference and has a 7 mm dark-grey cone collar at its base.
- **Back of the head**: a green light panel is sunk 3 mm into the sloped face. The lower edge of its recess is straight; the upper edge and the sides have bevels about 4 mm wide.
- **Torso**: seen from above, the sides narrow toward the front, and the edge between the top and the sides carries a bevel that widens toward the front. The grey chest plate sits 5.2 mm behind the front face, and a small red block sits where the front meets the sloped top. The back has a panel sunk 4 mm with bevelled edges. Each hip has a round recess with a narrow raised rim.
- **Thighs**: the thigh plate is a shallow tray, hollow on the inside, with a rolled rim all round. The outside has a channel whose floor is 1.5 mm below the plate face and dark brown, with a grey rod lying across it, thick at the top and thin at the bottom. The upper part of the channel has a red block almost flush with the plate and a hex pocket in it. A grey threaded piston sits in the side slot next to the channel. The axes, diameters and heights of the rod and piston come from circles fitted to reference cross-sections. The plate edge is a steep slope: the outer face is 1.25 mm smaller than the outline and slopes almost all the way to the inside. The knee bolt cap is revolved from the reference profile: a bevelled base, a step, a narrow groove, a boss and a round dimple in the middle, with a visible gap all round. The knee joint centre is placed at the fitted circle centre of the bolt cap.
- **Side paint**: the reference texture differs between the two sides, so this model does too. The right side (-y) has a grey side plate (with a red dot on it), a long red stripe near the top, a red block at the front, a red stripe at the lower back and a red block on the curved face of the snout. The left side (+y) has only one red stripe, lower down. Both sides have a narrow grey strip along the top edge that joins the grey band across the top of the head.
- **Shins**: the outer red plate stands 2.7 mm proud and has a lug at each end that stands 5.6 mm proud.
- **Feet**: the heel is thin and thickens toward the front to 5.3 mm, with a bevelled toe. The plate has two slots (leaving 0.4 mm at the bottom). The ankle fork is two odd-shaped side plates with a low crossbar between them. The back half of the foot is dark; the front half and the fork are light.

Where this model deliberately differs from the reference (so it can be printed and assembled):
- **Hip connection**: in the reference, the thigh and torso actually hang apart. Here the inside of each thigh has a hub hidden in the hip recess to carry the hip pin.
- **Fits**: inlay pockets have a 0.2 mm glue gap per side, the joints have 3.3 mm pin holes, and the antenna base has a 2.3 mm socket.
- **Foot slots**: the reference slot floor has zero thickness. The printed part keeps 0.4 mm.
- **Stand**: the reference has no stand, but the printed model cannot stand without one.

Where it cannot match exactly:
- **Mesh detail**: the reference is a sculpted mesh of 600,000 triangles; this is a FreeCAD solid. At the 0.5 mm comparison resolution, the remaining differences are one-pixel strips along part edges, a few 1–2 mm patches around the knees, and hidden mechanical detail inside recesses (such as the floor of the hip recess).
- **Texture detail**: dirt, scratches, gradients and colour patches smaller than about 3 mm exist only in the texture, not in the shape, so weathering has to be painted by hand.

## Licence and notices

- Scripts (`*.py`): MIT, see `LICENSE`.
- Model files (`BD1.FCStd`, the exported STLs, `preview.png`): CC BY-NC-SA 4.0, no commercial use, see `LICENSE-MODEL`. Do not sell prints.
- BD-1 is a character owned by Lucasfilm / Disney. This repository is unofficial, non-commercial fan work with no connection to them.
- The reference mesh used for measuring has no licence statement and is not in this repository (`ref/` and the reference folder are in `.gitignore`). Get your own copy, for personal use only.

## Files

| File | Purpose |
|---|---|
| `bd1_model.py` | Parametric model: dimensions, outlines, joint positions and fit clearances all live here |
| `BD1.FCStd` | FreeCAD assembly with colours |
| `stl/*.stl` | One STL per part (54), at its assembled position. Lay each part flat in your slicer before printing |
| `export_stl.py` | Regenerates the STLs |
| `preview_gui.py` | Regenerates the coloured `BD1.FCStd` and `preview.png` |
| `check_fit.py` | Checks that no parts intersect and prints the centre of mass |
| `glb_ref.py` | Reads the reference GLB (with skinning and texture colours), converts it to this project's coordinates and scale, and saves `ref/bd1_ref.npz` |
| `ref_profiles.py` | Traces 2D outlines of parts from the reference mesh, used to update the outline points in `bd1_model.py` |
| `render_views.py` | Renders front, side and top orthographic views of the model and the reference mesh into `views/` |
| `compare.py` | Compares the silhouettes and prints IoU, per-section deviation (mm) and overlay images |
| `depth_diff.py` | Compares surface height from six directions, writes difference images `views/depth_<direction>.png` and the largest differing regions (about 4 minutes). You can pass direction names, for example `depth_diff.py left front` |
| `heightmap.py` | Rasterises a triangle mesh into a height map; used by `depth_diff.py` and when measuring the reference mesh |

After changing dimensions, regenerate:

```bash
cd ~/bdx/openbd1 && /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd export_stl.py
```

Size is controlled by `BD1_HEIGHT`, the head-top height in mm, default 190. `BD1_HEIGHT=316` is close to life size. The shape scales as a whole, while pin holes, antenna holes and glue gaps keep their real size, so the hardware does not change.

The full printing and assembly steps, the parts list and the filament matching are in [PRINTING.en.md](PRINTING.en.md). To drag, explode and see the print-bed layout in a browser, see the "Web page" section below.

## Parts and colours

Colours come from the reference texture, as the area-weighted average over each surface.

| Colour | Value | Parts |
|---|---|---|
| Ivory | `#C9CFB0` | head_shell, neck, torso, antenna ×2 |
| Warm ivory | `#B2A696` | thigh ×2, ear ×2 |
| Warm grey | `#80786B` | shin ×2 |
| Grey | `#999996` | head_top_band, paint_*_top_edge, paint_right_panel, paint_*_hood_grey, chest_plate |
| Mid grey | `#82827D` | ear_centre ×2, knee_cap ×2, thigh_rod ×2, thigh_piston ×2 |
| Light grey | `#B8BAB0` | eye_ring_left |
| Lens grey | `#B2B5B2` | lens_left |
| Bright red | `#C40A08` | paint_right_stripe, paint_right_panel_dot, paint_right_front_block, paint_right_back_strip, paint_right_snout, paint_left_stripe, eye_band_right |
| Dark red | `#7A2B26` | shin_plate ×2, thigh_channel ×2 (the block at the top of the channel), chest_tab |
| Oxblood | `#5E3330` | eye_ring_right |
| Steel blue | `#638599` | lens_right (BD-1's own right eye, the larger one) |
| Green | `#52A624` | head_light |
| Dark brown | `#593D36` | thigh_channel_floor ×2, thigh_channel_tip ×2 |
| Dark grey | `#595952` | foot_heel ×2 |
| Pale sage | `#B2B59E` | foot_front ×2 |
| Charcoal | `#424242` | antenna_collar ×2 |
| Black-grey | `#33363B` | stand (not part of BD-1) |

## Assembly

- **Hardware**:
  - 3 mm steel rod, aluminium rod or M3 screws. Pin holes are 3.3 mm, the joints can turn, and they hold by friction.
    - Hip: one 3×65 mm pin through the left thigh, the torso and the right thigh.
    - Knee: one 3×8 mm pin per side, inserted from the inside of the shin; the outside is plugged by the short 3 mm peg on the knee_cap.
    - Ankle: one 3×12 mm pin per side, through the fork on the foot and the end of the shin.
  - Antenna: 2 mm brass rod, about 76 mm each. Slide on the antenna_collar cone first, then push it into the slanted 2.3 mm hole on the outer ear ring. You can use the printed antenna part instead, but it is only 2.1 mm thick and breaks easily.
- **Glued parts**: pockets have a 0.2 mm gap per side. Use CA glue or two-part epoxy.
  - Inlays go into 1 mm deep pockets: the top band, the paint_* pieces on both sides (the red and grey blocks on the hood follow its curved face), the red chest tab, and the red ring on the face of the right eye barrel. The light panel and the chest plate are glued to the floors of their own pockets. The red shin plate also goes into a 1 mm pocket but stands proud of the shin surface.
  - Thighs: first fit the dark channel floor, the small tip piece and the red block into the channel, then glue the rod to the channel floor (thick end below the hex pocket), glue the threaded piston into the side slot, and press the knee cap into the knee recess.
  - Eye barrels go into the 6 mm deep sockets in the face panel, then the lenses go into the barrels.
  - Ears: the grey centre piece goes into the side of the head by its own 3 mm peg, and the outer ring slides over it and is glued to the head.
  - Each end of the neck goes into an 8 mm slanted hole.
  - Feet: the dark rear half and the light front half are butt-glued at x = 40.5, with the ankle fork on the front half.
  - Hips: the hub on the inside of each thigh reaches into the round recess on the side of the torso, and the hip pin passes through the hub and the torso.
- **Stand (required)**: the centre of mass is about 4.5 mm behind the heel (centre of mass x 5.0, heel x 9.5), so two feet alone cannot stand. Glue the feet into the 1.2 mm recesses in the stand.

## Printing advice

- **Head shell**: the largest part, 137×111×40 mm. Print it lying on its side so the hood's top plate, side walls and panel are vertical and it needs almost no support. Model it solid, with 2–3 walls and 10–15 % infill.
- **Rods and threaded pistons**: print with the flat underside down. The thread ridges are only 0.25–0.3 mm, so a 0.2 mm nozzle or 0.08 mm layers will show them better. You can also cut a piece of 3 mm screw instead of printing the rod.
- **Leg parts and feet**: print lying on their sides, with layer lines running along the leg.
- **Thin inlays**: mostly 1 mm thick, print them flat. Use a 0.4 mm nozzle and 0.12–0.16 mm layers.
- **Painting**: prime first, then spray ivory. The red, grey and dark parts are separate pieces, so no masking is needed. Draw a red line in the thin groove on the outer ear ring. Finally fill the panel lines, the ear ring groove, the thigh side slot and the through-slots on the feet with dark grey panel-line wash.

## Web page

`web/` is a Vite project: a 3D model built from the real STLs that you can orbit, explode and lay out on the print beds, with every assembly step highlighting its parts. three.js and the fonts are installed from npm and bundled into the build, so the deployed page needs no CDN. The page is in Chinese and English: it follows the browser language by default, a button at the top right switches it, and the choice is remembered in the browser. All copy is in `web/src/i18n.js`; to change wording or add a language, edit that one file.

```bash
cd web
npm install
npm run dev        # local development, http://localhost:5173
npm run build      # output in web/dist, plain static files
```

Live address: https://openbd1.haiwang.ai/

**Deploying to GitHub Pages**: after pushing to GitHub, go to the repository's Settings → Pages and set Source to "GitHub Actions". After that, every push to `main` that touches `web/` runs `npm ci && npm run build` through `.github/workflows/pages.yml` and publishes `web/dist`. Asset paths are relative, so it works on a custom domain (this one uses `openbd1.haiwang.ai`) or under a sub-path such as `https://<user>.github.io/openbd1/`.

The page reads the compressed meshes in `web/public/data/`. That data is committed to the repository, so deployment does not need FreeCAD. After changing the model, regenerate it locally and commit:

```bash
cd ~/bdx/openbd1
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd export_stl.py
/Applications/FreeCAD.app/Contents/Resources/bin/python -I render_print_layout.py
/Applications/FreeCAD.app/Contents/Resources/bin/python -I pack_web.py
```

## Comparing with the reference mesh

```bash
cd ~/bdx/openbd1
/Applications/FreeCAD.app/Contents/Resources/bin/python -I glb_ref.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd render_views.py
/Applications/FreeCAD.app/Contents/Resources/bin/python compare.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd depth_diff.py
```

Both are aligned in world coordinates at 6 px/mm, so no fitting is needed and deviations read directly in mm.

Colours in `views/<view>_overlay.png`: grey is where the two coincide, red is where only the model is, and blue is where only the reference is. `views/<view>_ghost.png` overlays the textured reference and the model semi-transparently.

You can also compare from screenshots instead: put `front.png`, `side.png` and `top.png` in `ref/`, and `compare.py` will prefer them and search for scale, mirroring and shift automatically. Use a plain-colour background, or supply `ref/<view>_mask.png` as well.
