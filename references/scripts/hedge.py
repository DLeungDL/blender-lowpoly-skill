"""Parameterized low-poly hedge.

DNA is a *procedure with knobs*, not a vertex dump and not a CAD cube.
Look target: irregular tris, Shade Flat, one sage slot (~292 v / 521 f).

Cube -> scale -> bevel -> subsurf -> displace -> collapse -> fractal large faces.
Tune LENGTH/WIDTH/HEIGHT/CORNER/COLLAPSE_FACES/DISPLACE/FRACTAL. Do not paste GLB verts.
"""
import bpy
import random

LENGTH = 2.80
WIDTH = 0.95
HEIGHT = 1.10
CORNER = 0.20
SEGMENTS = 4
SUBSURF = 2
DISPLACE = 0.028
NOISE_SCALE = 0.55
COLLAPSE_FACES = 200
FRACTAL = 0.28
FRACTAL_NORMAL = 0.45
FRACTAL_AREA = 0.08
FRACTAL_SEED = 11
COLOR = (0.40, 0.46, 0.28, 1.0)
NAME = "Hedge"
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


def sit_on_ground(mesh, eps=0.015):
    minz = min(v.co.z for v in mesh.vertices)
    for v in mesh.vertices:
        v.co.z -= minz
        if v.co.z < eps:
            v.co.z = 0.0
    mesh.update()


def make_hedge(
    length=LENGTH,
    width=WIDTH,
    height=HEIGHT,
    corner=CORNER,
    segments=SEGMENTS,
    subsurf=SUBSURF,
    displace=DISPLACE,
    collapse_faces=COLLAPSE_FACES,
    fractal=FRACTAL,
    color=COLOR,
    name=NAME,
):
    col = ensure_collection(COLLECTION)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (length, width, height)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Move into the REF collection only.
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = corner
    bev.segments = segments
    bev.affect = "EDGES"
    bev.limit_method = "NONE"
    bpy.ops.object.modifier_apply(modifier="Bevel")

    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = subsurf
    sub.render_levels = subsurf
    sub.subdivision_type = "CATMULL_CLARK"
    bpy.ops.object.modifier_apply(modifier="Subsurf")

    tex = bpy.data.textures.get("HedgeNoise") or bpy.data.textures.new("HedgeNoise", "CLOUDS")
    tex.noise_scale = NOISE_SCALE
    tex.noise_depth = 2
    disp = obj.modifiers.new("Disp", "DISPLACE")
    disp.strength = displace
    disp.mid_level = 0.5
    disp.texture = tex
    disp.texture_coords = "LOCAL"
    bpy.ops.object.modifier_apply(modifier="Disp")

    n_dense = len(obj.data.polygons)
    dec = obj.modifiers.new("Decimate", "DECIMATE")
    dec.decimate_type = "COLLAPSE"
    dec.ratio = max(0.02, min(1.0, collapse_faces / float(max(1, n_dense))))
    bpy.ops.object.modifier_apply(modifier="Decimate")

    mesh = obj.data
    sit_on_ground(mesh)
    for p in mesh.polygons:
        p.use_smooth = False
        p.select = p.area > FRACTAL_AREA
    for v in mesh.vertices:
        v.select = False
    for e in mesh.edges:
        e.select = False

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(
        number_cuts=1,
        fractal=fractal,
        fractal_along_normal=FRACTAL_NORMAL,
        seed=FRACTAL_SEED,
    )
    bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY", ngon_method="BEAUTY")
    bpy.ops.object.mode_set(mode="OBJECT")

    sit_on_ground(mesh)
    for p in mesh.polygons:
        p.use_smooth = False
        p.select = False
    mesh.materials.clear()
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
        "path_note": "procedure knobs; look ~292v/521f irregular tris",
    })


if __name__ == "__main__":
    main()
