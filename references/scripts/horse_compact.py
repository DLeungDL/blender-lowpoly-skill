"""Horse compact reconstruction from Horse.glb.

Source: /workspace/refs/glb/Horse.glb (compact).
Measured: 1436 verts, 690 tris, 2 material slots, 28 bones.
Actions: Idle, Jump, Walk, WalkSlow, Run, Death.

This script builds a primitive approximation (cubes / 8-gon cylinders / cones)
placed at measured bone heads and material-island colours. Not a vertex clone.
"""

import bpy
from mathutils import Vector
from math import atan2, sqrt, pi

def _clear_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        return
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(col)

def _ensure_collection(name):
    _clear_collection(name)
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    # make it the active collection so primitives land here
    layer = bpy.context.view_layer.layer_collection
    def _find(lc, n):
        if lc.name == n:
            return lc
        for ch in lc.children:
            f = _find(ch, n)
            if f:
                return f
        return None
    found = _find(layer, name)
    if found:
        bpy.context.view_layer.active_layer_collection = found
    return col

def _link(col, obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    if obj.name not in col.objects:
        col.objects.link(obj)

def flat_mat(name, rgba):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = tuple(rgba)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 1.0
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = 1.0
    mat.diffuse_color = tuple(rgba)
    return mat

def shade_flat(obj):
    for p in obj.data.polygons:
        p.use_smooth = False

def _apply(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

def box(name, center, size, mat, col):
    """Cube with full-size (sx,sy,sz) centered at world center."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.scale = (size[0], size[1], size[2])
    _apply(obj)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    shade_flat(obj)
    _link(col, obj)
    return obj

def cyl(name, p0, p1, radius, mat, col, vertices=8):
    a = Vector(p0)
    b = Vector(p1)
    d = b - a
    length = d.length
    if length < 1e-6:
        length = 0.1
        d = Vector((0, 0, 0.1))
    mid = (a + b) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=length, location=mid
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    quat = Vector((0.0, 0.0, 1.0)).rotation_difference(d.normalized())
    obj.rotation_euler = quat.to_euler()
    _apply(obj)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    shade_flat(obj)
    _link(col, obj)
    return obj

def cone(name, p0, p1, r1, r2, mat, col, vertices=6):
    a = Vector(p0)
    b = Vector(p1)
    d = b - a
    length = max(d.length, 0.05)
    mid = (a + b) * 0.5
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=r1, radius2=r2, depth=length, location=mid
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    quat = Vector((0.0, 0.0, 1.0)).rotation_difference(d.normalized() if d.length > 1e-8 else Vector((0, 0, 1)))
    obj.rotation_euler = quat.to_euler()
    _apply(obj)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    shade_flat(obj)
    _link(col, obj)
    return obj

def join_weld(parts, name, col):
    import bmesh
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    shade_flat(obj)
    obj.data.transform(obj.matrix_world)
    obj.matrix_world.identity()
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    _link(col, obj)
    return obj

def make_armature(arm_name, bones, col, z_off=0.0):
    """bones: list of dicts {name, parent, head, tail} in measured world space."""
    # Prefer child-directed tails so tiny GLB joints become usable bones.
    children = {}
    by_name = {b["name"]: b for b in bones}
    for b in bones:
        p = b.get("parent")
        if p:
            children.setdefault(p, []).append(b["name"])
    arm_data = bpy.data.armatures.new(arm_name + "_Data")
    arm_obj = bpy.data.objects.new(arm_name, arm_data)
    col.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    ebones = arm_data.edit_bones
    created = {}
    for b in bones:
        h = Vector(b["head"])
        t = Vector(b["tail"])
        h.z += z_off
        t.z += z_off
        kids = children.get(b["name"], [])
        if kids:
            ch = Vector(by_name[kids[0]]["head"])
            ch.z += z_off
            if (ch - h).length > 0.04:
                t = ch
        if (t - h).length < 0.05:
            t = h + Vector((0.0, 0.0, 0.18))
        eb = ebones.new(b["name"])
        eb.head = h
        eb.tail = t
        eb.use_deform = True
        created[b["name"]] = eb
    for b in bones:
        p = b.get("parent")
        if p and p in created:
            created[b["name"]].parent = created[p]
            created[b["name"]].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj

def parent_mesh(mesh, arm):
    mesh.parent = arm
    mod = mesh.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    return mod


COL_NAME = 'REF_Horse_Compact'
MESH_NAME = 'Horse'
Z_OFF = -0.01846  # -measured_feet_z so feet land on Z=0

BONES = [
    {'name': 'root', 'parent': None, 'head': (0.00000, 0.00000, 0.00000), 'tail': (0.00000, 0.00000, 0.02113)},
    {'name': 'FrontFoot.R', 'parent': 'root', 'head': (-0.91177, -1.92702, 0.10000), 'tail': (-0.91177, -1.94815, 0.10000)},
    {'name': 'Body', 'parent': 'root', 'head': (0.00538, 0.01735, 2.30208), 'tail': (0.00538, 0.01735, 2.32277)},
    {'name': 'FrontLeg.R', 'parent': 'Body', 'head': (-0.31930, -1.85574, 3.14008), 'tail': (-0.32533, -1.85574, 3.14008)},
    {'name': 'FrontUpLeg.R', 'parent': 'FrontLeg.R', 'head': (-0.92186, -1.85574, 3.14008), 'tail': (-0.92186, -1.85817, 3.12548)},
    {'name': 'FrontLowLeg.R', 'parent': 'FrontUpLeg.R', 'head': (-0.92186, -2.09927, 1.67979), 'tail': (-0.92186, -2.09779, 1.66506)},
    {'name': 'BackLeg.R', 'parent': 'Body', 'head': (-0.31930, 2.19588, 3.14008), 'tail': (-0.32400, 2.19588, 3.14008)},
    {'name': 'BackUpLeg.R', 'parent': 'BackLeg.R', 'head': (-0.78889, 2.19588, 3.14008), 'tail': (-0.78889, 2.20224, 3.13126)},
    {'name': 'BackLowLeg.R', 'parent': 'BackUpLeg.R', 'head': (-0.78889, 2.83167, 2.25786), 'tail': (-0.78889, 2.83046, 2.24706)},
    {'name': 'FrontLeg.L', 'parent': 'Body', 'head': (0.26843, -1.85574, 3.14008), 'tail': (0.27445, -1.85574, 3.14008)},
    {'name': 'FrontUpLeg.L', 'parent': 'FrontLeg.L', 'head': (0.87098, -1.85574, 3.14008), 'tail': (0.87098, -1.85817, 3.12548)},
    {'name': 'FrontLowLeg.L', 'parent': 'FrontUpLeg.L', 'head': (0.87098, -2.09927, 1.67979), 'tail': (0.87098, -2.09779, 1.66506)},
    {'name': 'BackLeg.L', 'parent': 'Body', 'head': (0.26843, 2.19588, 3.14008), 'tail': (0.27312, 2.19588, 3.14008)},
    {'name': 'BackUpLeg.L', 'parent': 'BackLeg.L', 'head': (0.73801, 2.19588, 3.14008), 'tail': (0.73801, 2.20224, 3.13126)},
    {'name': 'BackLowLeg.L', 'parent': 'BackUpLeg.L', 'head': (0.73801, 2.83166, 2.25787), 'tail': (0.73801, 2.83046, 2.24706)},
    {'name': 'Back', 'parent': 'Body', 'head': (-0.02691, 2.41963, 3.70949), 'tail': (-0.02691, 2.40899, 3.71273)},
    {'name': 'Tail1', 'parent': 'Back', 'head': (-0.01574, 2.70068, 4.78580), 'tail': (-0.01574, 2.70905, 4.78536)},
    {'name': 'Tail2', 'parent': 'Tail1', 'head': (-0.01574, 3.53703, 4.74136), 'tail': (-0.01574, 3.53868, 4.73273)},
    {'name': 'Tail3', 'parent': 'Tail2', 'head': (-0.01574, 3.70194, 3.87910), 'tail': (-0.01574, 3.70120, 3.87215)},
    {'name': 'Tail4', 'parent': 'Tail3', 'head': (-0.01574, 3.62843, 3.18365), 'tail': (-0.01574, 3.62716, 3.17677)},
    {'name': 'Shoulders', 'parent': 'Body', 'head': (-0.06828, -1.83464, 4.10980), 'tail': (-0.06786, -1.84168, 4.12088)},
    {'name': 'Neck', 'parent': 'Shoulders', 'head': (-0.02691, -2.53868, 5.21816), 'tail': (-0.02691, -2.54788, 5.22814)},
    {'name': 'Head', 'parent': 'Neck', 'head': (-0.02690, -3.45826, 6.21652), 'tail': (-0.02693, -3.46962, 6.20909)},
    {'name': 'Hips', 'parent': 'Body', 'head': (-0.02691, 1.49155, 3.99190), 'tail': (-0.02691, 1.47689, 3.99138)},
    {'name': 'Torso', 'parent': 'Hips', 'head': (-0.02691, 0.02531, 3.93973), 'tail': (-0.02730, 0.01068, 3.94078)},
    {'name': 'BackFoot.R', 'parent': 'root', 'head': (-0.83586, 2.60472, 0.10000), 'tail': (-0.83586, 2.58359, 0.10000)},
    {'name': 'FrontFoot.L', 'parent': 'root', 'head': (0.86089, -1.92702, 0.10000), 'tail': (0.86089, -1.94815, 0.10000)},
    {'name': 'BackFoot.L', 'parent': 'root', 'head': (0.78499, 2.60472, 0.10000), 'tail': (0.78499, 2.58359, 0.10000)},
]


def vz(x, y, z):
    return (x, y, z + Z_OFF)


def build():
    col = _ensure_collection(COL_NAME)
    body_mat = flat_mat('Material.003', (0.1397, 0.0594, 0.0373, 1.0000))
    dark_mat = flat_mat('Material.006', (0.0163, 0.0163, 0.0163, 1.0000))
    parts = []

    # World (pre-shift): size 2.57 x 9.24 x 6.91, head -Y, feet Z~0.018
    # Slot0 Material.003 body brown 504 tris, bbox size 2.57 x 8.14 x 6.65
    # Slot1 Material.006 dark mane/tail/hooves 186 tris, bbox size 2.25 x 9.24 x 6.90
    body = box("Body", vz(0.0, 0.18, 3.95), (2.20, 4.70, 2.40), body_mat, col)
    chest = box("Chest", vz(0.0, -1.70, 4.05), (2.10, 1.60, 2.20), body_mat, col)
    rump = box("Rump", vz(0.0, 2.15, 4.00), (2.05, 1.50, 2.20), body_mat, col)
    neck = cyl("Neck", vz(0.0, -1.83, 4.11), vz(0.0, -3.20, 5.90), 0.55, body_mat, col, 8)
    head = box("Head", vz(0.0, -4.05, 6.15), (0.95, 1.70, 1.15), body_mat, col)
    snout = box("Snout", vz(0.0, -4.85, 5.70), (0.70, 0.85, 0.70), body_mat, col)
    ear_l = cone("Ear.L", vz(0.28, -3.55, 6.55), vz(0.38, -3.40, 6.92), 0.16, 0.04, body_mat, col, 5)
    ear_r = cone("Ear.R", vz(-0.28, -3.55, 6.55), vz(-0.38, -3.40, 6.92), 0.16, 0.04, body_mat, col, 5)
    mane = box("Mane", vz(0.0, -2.40, 5.85), (0.35, 2.40, 1.10), dark_mat, col)
    blaze = box("Blaze", vz(0.0, -4.20, 6.45), (0.18, 0.90, 0.35), dark_mat, col)
    tail = cyl("Tail", vz(0.0, 2.70, 4.79), vz(0.0, 3.85, 3.20), 0.22, dark_mat, col, 6)
    # legs: upper hip -> low, then low -> foot
    flu = cyl("FrontUpLeg.L", vz(0.871, -1.856, 3.14), vz(0.871, -2.099, 1.68), 0.28, body_mat, col, 8)
    fll = cyl("FrontLowLeg.L", vz(0.871, -2.099, 1.68), vz(0.861, -1.927, 0.28), 0.20, body_mat, col, 8)
    fru = cyl("FrontUpLeg.R", vz(-0.922, -1.856, 3.14), vz(-0.922, -2.099, 1.68), 0.28, body_mat, col, 8)
    frl = cyl("FrontLowLeg.R", vz(-0.922, -2.099, 1.68), vz(-0.912, -1.927, 0.28), 0.20, body_mat, col, 8)
    blu = cyl("BackUpLeg.L", vz(0.738, 2.196, 3.14), vz(0.738, 2.832, 2.26), 0.32, body_mat, col, 8)
    bll = cyl("BackLowLeg.L", vz(0.738, 2.832, 2.26), vz(0.785, 2.605, 0.28), 0.22, body_mat, col, 8)
    bru = cyl("BackUpLeg.R", vz(-0.789, 2.196, 3.14), vz(-0.789, 2.832, 2.26), 0.32, body_mat, col, 8)
    brl = cyl("BackLowLeg.R", vz(-0.789, 2.832, 2.26), vz(-0.836, 2.605, 0.28), 0.22, body_mat, col, 8)
    hfl = box("Hoof.FL", vz(0.861, -1.927, 0.12), (0.42, 0.55, 0.24), dark_mat, col)
    hfr = box("Hoof.FR", vz(-0.912, -1.927, 0.12), (0.42, 0.55, 0.24), dark_mat, col)
    hbl = box("Hoof.BL", vz(0.785, 2.605, 0.12), (0.42, 0.55, 0.24), dark_mat, col)
    hbr = box("Hoof.BR", vz(-0.836, 2.605, 0.12), (0.42, 0.55, 0.24), dark_mat, col)
    parts = [body, chest, rump, neck, head, snout, ear_l, ear_r, mane, blaze, tail,
             flu, fll, fru, frl, blu, bll, bru, brl, hfl, hfr, hbl, hbr]

    mesh = join_weld(parts, MESH_NAME, col)
    arm = make_armature(MESH_NAME + "_Armature", BONES, col, z_off=Z_OFF)
    parent_mesh(mesh, arm)
    mats = [m.name for m in mesh.data.materials]
    summary = {
        "ok": True,
        "name": mesh.name,
        "verts": len(mesh.data.vertices),
        "faces": len(mesh.data.polygons),
        "materials": mats,
        "path_note": "primitive reconstruction; not a vertex clone of the source GLB",
    }
    print(summary)
    return summary


if __name__ == "__main__":
    try:
        build()
    except Exception:
        import traceback, sys
        traceback.print_exc()
        sys.exit(1)
