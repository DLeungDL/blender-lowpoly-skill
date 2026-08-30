"""Parameterized low-poly hedge (distilled DNA, not a vertex dump).

Cube -> scale(length, width, height) -> sit on Z=0 -> bevel corners ->
optional along-normal jitter -> triangulate -> Shade Flat -> one sage slot.

Do not subsurf+collapse to copy a decimated AI mesh. Tune the knobs.
"""
import bpy
import bmesh
import random

LENGTH = 2.80
WIDTH = 0.95
HEIGHT = 1.10
CORNER = 0.20
SEGMENTS = 3
JITTER = 0.018
COLOR = (0.40, 0.46, 0.28, 1.0)
NAME = "Hedge"
SEED = 7
COLLECTION = "REF_Hedge"


def flat_mat(name, rgba):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 1.0
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    mat.diffuse_color = rgba
    return mat


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    return col


def make_hedge(
    length=LENGTH,
    width=WIDTH,
    height=HEIGHT,
    corner=CORNER,
    segments=SEGMENTS,
    jitter=JITTER,
    color=COLOR,
    name=NAME,
    seed=SEED,
):
    col = ensure_collection(COLLECTION)
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    if obj.name not in bpy.context.scene.collection.objects:
        pass

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= length
        v.co.y *= width
        v.co.z *= height
    minz = min(v.co.z for v in bm.verts)
    for v in bm.verts:
        v.co.z -= minz

    corner = min(corner, width * 0.45, height * 0.45, length * 0.45)
    bm.edges.ensure_lookup_table()
    bmesh.ops.bevel(
        bm,
        geom=list(bm.edges),
        offset=corner,
        offset_type="OFFSET",
        segments=segments,
        affect="EDGES",
        clamp_overlap=True,
    )

    bm.normal_update()
    rng = random.Random(seed)
    if jitter > 0:
        for v in bm.verts:
            n = v.normal.copy()
            if n.length < 1e-8:
                continue
            n.normalize()
            v.co += n * rng.uniform(-jitter, jitter)
            if v.co.z < 0.02:
                v.co.z = 0.0

    minz = min(v.co.z for v in bm.verts)
    for v in bm.verts:
        v.co.z -= minz
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    for f in bm.faces:
        f.smooth = False
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    mesh.materials.append(flat_mat("Mat_Hedge", color))
    obj.location = (0.0, 0.0, 0.0)
    return obj


def main():
    obj = make_hedge()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    print({
        "ok": True,
        "name": obj.name,
        "verts": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
        "materials": [m.name for m in obj.data.materials],
        "path_note": "parameterized; tune LENGTH/WIDTH/HEIGHT/CORNER/JITTER",
    })


if __name__ == "__main__":
    main()
