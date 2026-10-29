"""Load the downloaded BD-1 GLB as a reference mesh, in this project's axes and mm.

Run with the FreeCAD Python (numpy):
  /Applications/FreeCAD.app/Contents/Resources/bin/python -I glb_ref.py
Writes ref/bd1_ref.npz: one triangle array per mesh node (and "<name>#rgb", the
texture colour at each triangle's centre, 0..1), in mm, X forward,
Y to BD-1's left, Z up, feet on Z=0, scaled so the top of the head shell is
at REF_HEAD_TOP_MM (the same head top as bd1_model at the current BD1_HEIGHT).
"""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GLB = os.path.join(HERE, "bd-1-droid-star-wars-jedi-fallen-order", "source", "BD1.glb")
OUT = os.path.join(HERE, "ref", "bd1_ref.npz")
SKIP = {"Cube"}            # backdrop box in the source scene
HEAD_NODE = "HEAD"
REF_HEAD_TOP_MM = float(os.environ.get("BD1_HEIGHT", "190"))

COMP = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    with open(path, "rb") as f:
        magic, _, _ = struct.unpack("<4sII", f.read(12))
        if magic != b"glTF":
            raise ValueError("not a GLB file")
        n, _ = struct.unpack("<I4s", f.read(8))
        gltf = json.loads(f.read(n))
        n, _ = struct.unpack("<I4s", f.read(8))
        blob = f.read(n)
    return gltf, blob


def accessor(gltf, blob, i):
    a = gltf["accessors"][i]
    bv = gltf["bufferViews"][a["bufferView"]]
    dt = np.dtype(COMP[a["componentType"]])
    k = NCOMP[a["type"]]
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0)
    if stride and stride != k * dt.itemsize:
        raw = np.frombuffer(blob, np.uint8, a["count"] * stride, off).reshape(-1, stride)
        arr = raw[:, :k * dt.itemsize].copy().view(dt)
    else:
        arr = np.frombuffer(blob, dt, a["count"] * k, off)
    arr = arr.reshape(a["count"], k) if k > 1 else arr
    if a.get("normalized"):
        arr = arr.astype(np.float64) / np.iinfo(dt).max
    return arr


def local_matrix(node):
    if "matrix" in node:
        return np.array(node["matrix"], float).reshape(4, 4).T
    t = np.array(node.get("translation", [0, 0, 0]), float)
    x, y, z, w = node.get("rotation", [0, 0, 0, 1])
    s = np.array(node.get("scale", [1, 1, 1]), float)
    r = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])
    m = np.eye(4)
    m[:3, :3] = r * s
    m[:3, 3] = t
    return m


def world_matrices(gltf):
    nodes = gltf["nodes"]
    world = [None] * len(nodes)

    def walk(i, parent):
        world[i] = parent @ local_matrix(nodes[i])
        for c in nodes[i].get("children", []):
            walk(c, world[i])

    for root in gltf["scenes"][gltf.get("scene", 0)]["nodes"]:
        walk(root, np.eye(4))
    return world


def base_colour_image(gltf, blob, material):
    """The material's base-colour texture as an RGB float array, or a flat colour."""
    pbr = gltf["materials"][material].get("pbrMetallicRoughness", {})
    if "baseColorTexture" not in pbr:
        return np.array(pbr.get("baseColorFactor", [1, 1, 1, 1])[:3], float)
    img = gltf["images"][gltf["textures"][pbr["baseColorTexture"]["index"]]["source"]]
    if "bufferView" in img:
        bv = gltf["bufferViews"][img["bufferView"]]
        import io
        data = io.BytesIO(blob[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]])
    else:
        data = os.path.join(os.path.dirname(GLB), img["uri"])
    im = Image.open(data).convert("RGB")
    im.thumbnail((1024, 1024))
    return np.asarray(im, float) / 255.0


def sample(tex, uv):
    if tex.ndim == 1:
        return np.tile(tex, (len(uv), 1))
    h, w, _ = tex.shape
    u = np.mod(uv[:, 0], 1.0) * (w - 1)
    v = np.mod(uv[:, 1], 1.0) * (h - 1)
    return tex[v.astype(int), u.astype(int)]


def mesh_triangles(gltf, blob, world):
    """Skinned triangles per mesh node in glTF world space (Y up), and their colours."""
    out, colours, textures = {}, {}, {}
    for ni, node in enumerate(gltf["nodes"]):
        if "mesh" not in node or node["name"] in SKIP or world[ni] is None:
            continue
        tris, cols = [], []
        for prim in gltf["meshes"][node["mesh"]]["primitives"]:
            att = prim["attributes"]
            pos = accessor(gltf, blob, att["POSITION"]).astype(np.float64)
            ph = np.c_[pos, np.ones(len(pos))]
            if "skin" in node and "JOINTS_0" in att:
                skin = gltf["skins"][node["skin"]]
                inv = accessor(gltf, blob, skin["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
                joint_m = np.stack([world[j] @ inv[k] for k, j in enumerate(skin["joints"])])
                jt = accessor(gltf, blob, att["JOINTS_0"]).astype(int)
                wt = accessor(gltf, blob, att["WEIGHTS_0"]).astype(np.float64)
                wt /= wt.sum(axis=1, keepdims=True)
                p = np.zeros_like(ph)
                for c in range(4):
                    p += wt[:, c:c + 1] * np.einsum("nij,nj->ni", joint_m[jt[:, c]], ph)
            else:
                p = ph @ world[ni].T
            idx = accessor(gltf, blob, prim["indices"]).astype(int).reshape(-1, 3)
            tris.append(p[:, :3][idx])
            mat = prim.get("material", 0)
            if mat not in textures:
                textures[mat] = base_colour_image(gltf, blob, mat)
            if "TEXCOORD_0" in att:
                uv = accessor(gltf, blob, att["TEXCOORD_0"]).astype(np.float64)[idx].mean(axis=1)
            else:
                uv = np.zeros((len(idx), 2))
            cols.append(sample(textures[mat], uv))
        out[node["name"]] = np.concatenate(tris)
        colours[node["name"]] = np.concatenate(cols)
    return out, colours


def main():
    gltf, blob = read_glb(GLB)
    world = world_matrices(gltf)
    meshes, colours = mesh_triangles(gltf, blob, world)
    # glTF: +Y up, face towards +Z, BD-1's left towards +X  ->  ours: X fwd, Y left, Z up.
    meshes = {k: v[..., [2, 0, 1]] for k, v in meshes.items()}
    allv = np.concatenate([v.reshape(-1, 3) for v in meshes.values()])
    floor = allv[:, 2].min()
    head_top = meshes[HEAD_NODE][..., 2].max()
    k = REF_HEAD_TOP_MM / (head_top - floor)
    centre = (allv[:, 0].min() + allv[:, 0].max()) / 2, (allv[:, 1].min() + allv[:, 1].max()) / 2
    for name in meshes:
        v = meshes[name]
        v = (v - np.array([centre[0], centre[1], floor])) * k
        meshes[name] = v
        lo, hi = v.reshape(-1, 3).min(0), v.reshape(-1, 3).max(0)
        print(f"{name:12s} tris {len(v):7d}  x {lo[0]:7.1f}..{hi[0]:6.1f}  "
              f"y {lo[1]:7.1f}..{hi[1]:6.1f}  z {lo[2]:6.1f}..{hi[2]:6.1f} mm")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    np.savez_compressed(OUT, **meshes, **{k + "#rgb": v for k, v in colours.items()})
    print(f"scale {k:.3f} mm per source unit; head top {REF_HEAD_TOP_MM:.0f} mm")


if __name__ == "__main__":
    sys.exit(main())
