"""Horse detailed reconstruction from Horse.glb (glb2).

Source: /workspace/refs/glb2/Horse.glb (detailed).
Measured: 4400 verts, 2182 tris, 8 slots (Main, Hair, Main_Dark, Muzzle,
Hooves, Main_Light, Eye_Black, Eye_White), 50 bones, 26 actions.

Localized islands (muzzle, blaze, eyes, hooves) are placed at measured
centroids/bboxes. Body volumes follow bone heads. Approximation, not a clone.
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


COL_NAME = 'REF_Horse_Detailed'
MESH_NAME = 'Horse'
Z_OFF = 0.01122  # -measured_feet_z so feet land on Z=0

BONES = [
    {'name': 'Body', 'parent': None, 'head': (0.00000, -0.00175, 0.91207), 'tail': (0.00000, -0.00175, 0.93858)},
    {'name': 'Back', 'parent': 'Body', 'head': (-0.00000, 1.43373, 3.14025), 'tail': (-0.00000, 1.42657, 3.13737)},
    {'name': 'Torso', 'parent': 'Back', 'head': (0.00000, 0.71785, 2.85317), 'tail': (0.00000, 0.70974, 2.85211)},
    {'name': 'Torso2', 'parent': 'Torso', 'head': (0.00000, -0.09231, 2.74692), 'tail': (0.00000, -0.10161, 2.74683)},
    {'name': 'Torso3', 'parent': 'Torso2', 'head': (-0.00000, -1.02254, 2.73790), 'tail': (-0.00000, -1.02719, 2.73946)},
    {'name': 'Neck1', 'parent': 'Torso3', 'head': (-0.00000, -1.48704, 2.89340), 'tail': (-0.00000, -1.48974, 2.89657)},
    {'name': 'Neck2', 'parent': 'Neck1', 'head': (-0.00000, -1.75682, 3.21071), 'tail': (-0.00000, -1.76060, 3.21544)},
    {'name': 'Neck3', 'parent': 'Neck2', 'head': (-0.00000, -2.13462, 3.68324), 'tail': (-0.00000, -2.13854, 3.68818)},
    {'name': 'Head', 'parent': 'Neck3', 'head': (-0.00000, -2.52645, 4.17718), 'tail': (-0.00000, -2.53156, 4.17348)},
    {'name': 'Ear1.L', 'parent': 'Head', 'head': (0.17729, -2.53625, 4.29079), 'tail': (0.17771, -2.53708, 4.29702)},
    {'name': 'Ear2.L', 'parent': 'Ear1.L', 'head': (0.18739, -2.55605, 4.43904), 'tail': (0.18912, -2.55705, 4.44502)},
    {'name': 'Ear3.L', 'parent': 'Ear2.L', 'head': (0.21624, -2.57262, 4.53829), 'tail': (0.21714, -2.57460, 4.54421)},
    {'name': 'Ear4.L', 'parent': 'Ear3.L', 'head': (0.23355, -2.61061, 4.65183), 'tail': (0.23475, -2.61258, 4.65770)},
    {'name': 'Ear1.R', 'parent': 'Head', 'head': (-0.17729, -2.53625, 4.29079), 'tail': (-0.17771, -2.53708, 4.29702)},
    {'name': 'Ear2.R', 'parent': 'Ear1.R', 'head': (-0.18739, -2.55605, 4.43904), 'tail': (-0.18912, -2.55705, 4.44502)},
    {'name': 'Ear3.R', 'parent': 'Ear2.R', 'head': (-0.21624, -2.57262, 4.53829), 'tail': (-0.21714, -2.57460, 4.54421)},
    {'name': 'Ear4.R', 'parent': 'Ear3.R', 'head': (-0.23355, -2.61061, 4.65183), 'tail': (-0.23475, -2.61258, 4.65770)},
    {'name': 'FrontShoulder.L', 'parent': 'Torso2', 'head': (0.22146, -1.35844, 2.33742), 'tail': (0.23068, -1.35844, 2.33863)},
    {'name': 'FrontUpperLeg.L', 'parent': 'FrontShoulder.L', 'head': (0.41948, -1.35844, 2.36349), 'tail': (0.41948, -1.35893, 2.35164)},
    {'name': 'FrontLowerLeg.L', 'parent': 'FrontUpperLeg.L', 'head': (0.41948, -1.40703, 1.17849), 'tail': (0.41948, -1.40562, 1.16671)},
    {'name': 'FrontShoulder.R', 'parent': 'Torso2', 'head': (-0.22146, -1.35845, 2.33742), 'tail': (-0.23068, -1.35845, 2.33863)},
    {'name': 'FrontUpperLeg.R', 'parent': 'FrontShoulder.R', 'head': (-0.41948, -1.35844, 2.36349), 'tail': (-0.41948, -1.35893, 2.35164)},
    {'name': 'FrontLowerLeg.R', 'parent': 'FrontUpperLeg.R', 'head': (-0.41948, -1.40703, 1.17849), 'tail': (-0.41948, -1.40562, 1.16671)},
    {'name': 'BackShoulder.L', 'parent': 'Back', 'head': (0.08888, 1.24263, 2.94539), 'tail': (0.09657, 1.24263, 2.94600)},
    {'name': 'BackLeg.L', 'parent': 'BackShoulder.L', 'head': (0.41899, 1.24263, 2.97147), 'tail': (0.41899, 1.23973, 2.96377)},
    {'name': 'BackUpperLeg.L', 'parent': 'BackLeg.L', 'head': (0.41899, 0.95313, 2.20209), 'tail': (0.41899, 0.96207, 2.19332)},
    {'name': 'BackLowerLeg.L', 'parent': 'BackUpperLeg.L', 'head': (0.41899, 1.84739, 1.32531), 'tail': (0.41899, 1.84707, 1.31279)},
    {'name': 'BackShoulder.R', 'parent': 'Back', 'head': (-0.08888, 1.24263, 2.94539), 'tail': (-0.09657, 1.24263, 2.94600)},
    {'name': 'BackLeg.R', 'parent': 'BackShoulder.R', 'head': (-0.41899, 1.24263, 2.97147), 'tail': (-0.41899, 1.23973, 2.96377)},
    {'name': 'BackUpperLeg.R', 'parent': 'BackLeg.R', 'head': (-0.41899, 0.95313, 2.20209), 'tail': (-0.41899, 0.96208, 2.19332)},
    {'name': 'BackLowerLeg.R', 'parent': 'BackUpperLeg.R', 'head': (-0.41899, 1.84739, 1.32531), 'tail': (-0.41899, 1.84707, 1.31279)},
    {'name': 'Tail1', 'parent': 'Back', 'head': (-0.00000, 1.43373, 3.14025), 'tail': (-0.00000, 1.44048, 3.14398)},
    {'name': 'Tail2', 'parent': 'Tail1', 'head': (-0.00000, 1.70495, 3.29058), 'tail': (-0.00000, 1.71116, 3.28600)},
    {'name': 'Tail3', 'parent': 'Tail2', 'head': (0.00000, 1.92538, 3.12813), 'tail': (0.00000, 1.92675, 3.12408)},
    {'name': 'Tail4', 'parent': 'Tail3', 'head': (0.00000, 2.06209, 2.72366), 'tail': (0.00000, 2.06178, 2.71940)},
    {'name': 'Tail5', 'parent': 'Tail4', 'head': (0.00000, 2.03952, 2.41262), 'tail': (0.00000, 2.03938, 2.40835)},
    {'name': 'Tail6', 'parent': 'Tail5', 'head': (0.00000, 2.02794, 2.06715), 'tail': (0.00000, 2.02835, 2.06313)},
    {'name': 'Tail7', 'parent': 'Tail6', 'head': (0.00000, 2.06970, 1.66501), 'tail': (0.00000, 2.07175, 1.66153)},
    {'name': 'PoleTargetBack.L', 'parent': 'Body', 'head': (0.41899, -3.78873, 0.90103), 'tail': (0.41899, -3.78873, 0.92753)},
    {'name': 'PoleTarget.L', 'parent': 'Body', 'head': (0.41948, -3.23262, 0.90480), 'tail': (0.41948, -3.23262, 0.93130)},
    {'name': 'PoleTargetBack.R', 'parent': 'Body', 'head': (-0.41899, -3.78873, 0.90103), 'tail': (-0.41899, -3.78873, 0.92753)},
    {'name': 'PoleTarget.R', 'parent': 'Body', 'head': (-0.41948, -3.23262, 0.90480), 'tail': (-0.41948, -3.23262, 0.93130)},
    {'name': 'IKBackLeg.L', 'parent': None, 'head': (0.41899, 1.82320, 0.39357), 'tail': (0.41899, 1.81618, 0.37579)},
    {'name': 'FFB.L', 'parent': 'IKBackLeg.L', 'head': (0.41899, 1.72439, 0.14325), 'tail': (0.41899, 1.71809, 0.12520)},
    {'name': 'IKFrontLeg.L', 'parent': None, 'head': (0.41948, -1.31292, 0.39357), 'tail': (0.41948, -1.31818, 0.38024)},
    {'name': 'FF.L', 'parent': 'IKFrontLeg.L', 'head': (0.41948, -1.41172, 0.14325), 'tail': (0.41948, -1.41645, 0.12972)},
    {'name': 'IKBackLeg.R', 'parent': None, 'head': (-0.41899, 1.82320, 0.39357), 'tail': (-0.41899, 1.81618, 0.37579)},
    {'name': 'FFB.R', 'parent': 'IKBackLeg.R', 'head': (-0.41899, 1.72439, 0.14325), 'tail': (-0.41899, 1.71809, 0.12520)},
    {'name': 'IKFrontLeg.R', 'parent': None, 'head': (-0.41948, -1.31292, 0.39357), 'tail': (-0.41948, -1.31818, 0.38024)},
    {'name': 'FF.R', 'parent': 'IKFrontLeg.R', 'head': (-0.41948, -1.41172, 0.14325), 'tail': (-0.41948, -1.41645, 0.12972)},
]


def vz(x, y, z):
    return (x, y, z + Z_OFF)


def build():
    col = _ensure_collection(COL_NAME)
    main_mat = flat_mat('Main', (0.1568, 0.0713, 0.0256, 1.0000))
    hair_mat = flat_mat('Hair', (0.0317, 0.0317, 0.0317, 1.0000))
    dark_mat = flat_mat('Main_Dark', (0.0885, 0.0419, 0.0165, 1.0000))
    muz_mat = flat_mat('Muzzle', (0.0376, 0.0275, 0.0154, 1.0000))
    hoof_mat = flat_mat('Hooves', (0.1178, 0.1054, 0.0872, 1.0000))
    light_mat = flat_mat('Main_Light', (0.2611, 0.1163, 0.0402, 1.0000))
    eye_b_mat = flat_mat('Eye_Black', (0.0072, 0.0072, 0.0072, 1.0000))
    eye_w_mat = flat_mat('Eye_White', (0.3895, 0.3895, 0.3895, 1.0000))
    parts = []

    # Detailed horse: 8 slots. World size 1.41 x 5.68 x 4.82, feet_z -0.011
    # Main 1532, Hair 254, Main_Dark 60, Muzzle 50, Hooves 88, Main_Light 152, Eye_Black 40, Eye_White 6
    body = box("Body", vz(0.0, -0.09, 2.75), (1.15, 2.60, 1.50), main_mat, col)
    chest = box("Chest", vz(0.0, -1.10, 2.74), (1.20, 1.10, 1.45), main_mat, col)
    rump = box("Rump", vz(0.0, 1.10, 2.95), (1.10, 1.20, 1.40), main_mat, col)
    neck = cyl("Neck", vz(0.0, -1.49, 2.89), vz(0.0, -2.40, 3.95), 0.32, main_mat, col, 8)
    head = box("Head", vz(0.0, -2.70, 4.10), (0.52, 0.70, 0.70), main_mat, col)
    # Main_Light blaze island: size 0.66 x 0.43 x 0.77 at centroid (0, -2.78, 4.40)
    blaze = box("Blaze", vz(0.0, -2.780, 4.395), (0.40, 0.43, 0.55), light_mat, col)
    # Main_Dark face: size 0.51 x 0.83 x 0.86 at (0, -3.10, 4.05)
    face_d = box("FaceDark", vz(0.0, -3.098, 4.052), (0.40, 0.50, 0.50), dark_mat, col)
    # Muzzle island: size 0.33 x 0.30 x 0.33 at (0, -3.31, 3.50)
    muzzle = box("Muzzle", vz(0.0, -3.311, 3.498), (0.333, 0.296, 0.331), muz_mat, col)
    # Eyes: Eye_Black size 0.56 x 0.09 x 0.08 at y=-2.924 z=4.146 (pair at x=+-0.27)
    ebl = box("EyeBlack.L", vz(0.270, -2.924, 4.146), (0.06, 0.09, 0.08), eye_b_mat, col)
    ebr = box("EyeBlack.R", vz(-0.270, -2.924, 4.146), (0.06, 0.09, 0.08), eye_b_mat, col)
    ewl = box("EyeWhite.L", vz(0.253, -2.918, 4.164), (0.020, 0.033, 0.016), eye_w_mat, col)
    ewr = box("EyeWhite.R", vz(-0.253, -2.918, 4.164), (0.020, 0.033, 0.016), eye_w_mat, col)
    ear_l = cone("Ear.L", vz(0.177, -2.536, 4.291), vz(0.234, -2.611, 4.652), 0.07, 0.02, main_mat, col, 5)
    ear_r = cone("Ear.R", vz(-0.177, -2.536, 4.291), vz(-0.234, -2.611, 4.652), 0.07, 0.02, main_mat, col, 5)
    # Hair: mane along neck (narrow X=0.43) + tail
    mane = box("Mane", vz(0.0, -1.90, 3.70), (0.28, 1.80, 0.70), hair_mat, col)
    tail = cyl("Tail", vz(0.0, 1.43, 3.14), vz(0.0, 2.07, 1.67), 0.12, hair_mat, col, 6)
    flu = cyl("FrontUpLeg.L", vz(0.419, -1.358, 2.36), vz(0.419, -1.407, 1.18), 0.14, main_mat, col, 8)
    fll = cyl("FrontLowLeg.L", vz(0.419, -1.407, 1.18), vz(0.419, -1.412, 0.22), 0.10, main_mat, col, 8)
    fru = cyl("FrontUpLeg.R", vz(-0.419, -1.358, 2.36), vz(-0.419, -1.407, 1.18), 0.14, main_mat, col, 8)
    frl = cyl("FrontLowLeg.R", vz(-0.419, -1.407, 1.18), vz(-0.419, -1.412, 0.22), 0.10, main_mat, col, 8)
    blu = cyl("BackUpLeg.L", vz(0.419, 1.243, 2.97), vz(0.419, 0.953, 2.20), 0.16, main_mat, col, 8)
    bll = cyl("BackLowLeg.L", vz(0.419, 0.953, 2.20), vz(0.419, 1.847, 1.33), 0.12, main_mat, col, 8)
    blc = cyl("BackCanon.L", vz(0.419, 1.847, 1.33), vz(0.419, 1.724, 0.22), 0.10, main_mat, col, 8)
    bru = cyl("BackUpLeg.R", vz(-0.419, 1.243, 2.97), vz(-0.419, 0.953, 2.20), 0.16, main_mat, col, 8)
    brl = cyl("BackLowLeg.R", vz(-0.419, 0.953, 2.20), vz(-0.419, 1.847, 1.33), 0.12, main_mat, col, 8)
    brc = cyl("BackCanon.R", vz(-0.419, 1.847, 1.33), vz(-0.419, 1.724, 0.22), 0.10, main_mat, col, 8)
    # Hooves slot size 1.08 x 3.47 x 0.22, z centroid 0.044
    hfl = box("Hoof.FL", vz(0.419, -1.412, 0.11), (0.22, 0.24, 0.22), hoof_mat, col)
    hfr = box("Hoof.FR", vz(-0.419, -1.412, 0.11), (0.22, 0.24, 0.22), hoof_mat, col)
    hbl = box("Hoof.BL", vz(0.419, 1.724, 0.11), (0.22, 0.24, 0.22), hoof_mat, col)
    hbr = box("Hoof.BR", vz(-0.419, 1.724, 0.11), (0.22, 0.24, 0.22), hoof_mat, col)
    parts = [body, chest, rump, neck, head, blaze, face_d, muzzle, ebl, ebr, ewl, ewr,
             ear_l, ear_r, mane, tail, flu, fll, fru, frl, blu, bll, blc, bru, brl, brc,
             hfl, hfr, hbl, hbr]

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
