"""BBox reconstruction (NOT a vertex clone) of the detailed white horse.

Source GLB: /workspace/refs/glb2/White Horse.glb
Tier: detailed
Measured: 4400 verts, 2182 tris, 7 material slots, 50 bones.

Each material island is one cube at the measured world bbox centroid
with the measured bbox size and Principled Base Color albedo.
Shade Flat, roughness 1, alpha 1. Joined into one mesh.
Origin at (0, 0, 0); feet stay near Z=0.
Optional armature uses the real bone names (approximate chain).
"""
import bpy
from mathutils import Vector


COLLECTION = 'REF_Horse_White'
MESH_NAME = 'Horse_White'
ARM_NAME = 'Horse_White_Armature'
TIER = 'detailed'
SOURCE_TRIS = 2182
SOURCE_VERTS = 4400
SOURCE_SLOTS = 7
SOURCE_BONES = 50
SOURCE_GLB = '/workspace/refs/glb2/White Horse.glb'

SLOTS = [
    {
        "name": 'Main',
        "rgba": (0.3543, 0.3584, 0.2911, 1.0000),
        "centroid": (0.0000, -0.7483, 2.4489),
        "size": (1.4069, 5.3694, 4.7276),
        "tris": 1592,
        "albedo_source": 'principled',
    },
    {
        "name": 'Hair',
        "rgba": (0.3288, 0.2799, 0.1968, 1.0000),
        "centroid": (0.0000, -0.3747, 3.0124),
        "size": (0.4340, 5.1960, 3.1278),
        "tris": 254,
        "albedo_source": 'principled',
    },
    {
        "name": 'Muzzle',
        "rgba": (0.2487, 0.1618, 0.0977, 1.0000),
        "centroid": (0.0000, -3.3048, 3.5377),
        "size": (0.3329, 0.2960, 0.3310),
        "tris": 50,
        "albedo_source": 'principled',
    },
    {
        "name": 'Hooves',
        "rgba": (0.2306, 0.1825, 0.0665, 1.0000),
        "centroid": (0.0000, 0.0805, 0.0986),
        "size": (1.0822, 3.4707, 0.2197),
        "tris": 88,
        "albedo_source": 'principled',
    },
    {
        "name": 'Main_Light',
        "rgba": (0.2306, 0.2212, 0.2283, 1.0000),
        "centroid": (0.0000, -2.8052, 4.4302),
        "size": (0.6578, 0.4269, 0.7651),
        "tris": 152,
        "albedo_source": 'principled',
    },
    {
        "name": 'Eye_Black',
        "rgba": (0.0072, 0.0072, 0.0072, 1.0000),
        "centroid": (0.0000, -2.9213, 4.1379),
        "size": (0.5581, 0.0907, 0.0808),
        "tris": 40,
        "albedo_source": 'principled',
    },
    {
        "name": 'Eye_White',
        "rgba": (0.3895, 0.3895, 0.3895, 1.0000),
        "centroid": (0.0000, -2.9155, 4.1632),
        "size": (0.5404, 0.0472, 0.0200),
        "tris": 6,
        "albedo_source": 'principled',
    },
]

BONES = [
    {"name": 'Body', "parent": None, "head": (0.0000, -0.0018, 0.9121)},
    {"name": 'Back', "parent": 'Body', "head": (-0.0000, 1.4337, 3.1402)},
    {"name": 'Torso', "parent": 'Back', "head": (0.0000, 0.7178, 2.8532)},
    {"name": 'Torso2', "parent": 'Torso', "head": (0.0000, -0.0923, 2.7469)},
    {"name": 'Torso3', "parent": 'Torso2', "head": (-0.0000, -1.0225, 2.7379)},
    {"name": 'Neck1', "parent": 'Torso3', "head": (-0.0000, -1.4870, 2.8934)},
    {"name": 'Neck2', "parent": 'Neck1', "head": (-0.0000, -1.7568, 3.2107)},
    {"name": 'Neck3', "parent": 'Neck2', "head": (-0.0000, -2.1346, 3.6832)},
    {"name": 'Head', "parent": 'Neck3', "head": (-0.0000, -2.5265, 4.1772)},
    {"name": 'Ear1.L', "parent": 'Head', "head": (0.1773, -2.5362, 4.2908)},
    {"name": 'Ear2.L', "parent": 'Ear1.L', "head": (0.1874, -2.5560, 4.4390)},
    {"name": 'Ear3.L', "parent": 'Ear2.L', "head": (0.2162, -2.5726, 4.5383)},
    {"name": 'Ear4.L', "parent": 'Ear3.L', "head": (0.2336, -2.6106, 4.6518)},
    {"name": 'Ear1.R', "parent": 'Head', "head": (-0.1773, -2.5362, 4.2908)},
    {"name": 'Ear2.R', "parent": 'Ear1.R', "head": (-0.1874, -2.5560, 4.4390)},
    {"name": 'Ear3.R', "parent": 'Ear2.R', "head": (-0.2162, -2.5726, 4.5383)},
    {"name": 'Ear4.R', "parent": 'Ear3.R', "head": (-0.2336, -2.6106, 4.6518)},
    {"name": 'FrontShoulder.L', "parent": 'Torso2', "head": (0.2215, -1.3584, 2.3374)},
    {"name": 'FrontUpperLeg.L', "parent": 'FrontShoulder.L', "head": (0.4195, -1.3584, 2.3635)},
    {"name": 'FrontLowerLeg.L', "parent": 'FrontUpperLeg.L', "head": (0.4195, -1.4070, 1.1785)},
    {"name": 'FrontShoulder.R', "parent": 'Torso2', "head": (-0.2215, -1.3584, 2.3374)},
    {"name": 'FrontUpperLeg.R', "parent": 'FrontShoulder.R', "head": (-0.4195, -1.3584, 2.3635)},
    {"name": 'FrontLowerLeg.R', "parent": 'FrontUpperLeg.R', "head": (-0.4195, -1.4070, 1.1785)},
    {"name": 'BackShoulder.L', "parent": 'Back', "head": (0.0889, 1.2426, 2.9454)},
    {"name": 'BackLeg.L', "parent": 'BackShoulder.L', "head": (0.4190, 1.2426, 2.9715)},
    {"name": 'BackUpperLeg.L', "parent": 'BackLeg.L', "head": (0.4190, 0.9531, 2.2021)},
    {"name": 'BackLowerLeg.L', "parent": 'BackUpperLeg.L', "head": (0.4190, 1.8474, 1.3253)},
    {"name": 'BackShoulder.R', "parent": 'Back', "head": (-0.0889, 1.2426, 2.9454)},
    {"name": 'BackLeg.R', "parent": 'BackShoulder.R', "head": (-0.4190, 1.2426, 2.9715)},
    {"name": 'BackUpperLeg.R', "parent": 'BackLeg.R', "head": (-0.4190, 0.9531, 2.2021)},
    {"name": 'BackLowerLeg.R', "parent": 'BackUpperLeg.R', "head": (-0.4190, 1.8474, 1.3253)},
    {"name": 'Tail1', "parent": 'Back', "head": (-0.0000, 1.4337, 3.1402)},
    {"name": 'Tail2', "parent": 'Tail1', "head": (-0.0000, 1.7049, 3.2906)},
    {"name": 'Tail3', "parent": 'Tail2', "head": (0.0000, 1.9254, 3.1281)},
    {"name": 'Tail4', "parent": 'Tail3', "head": (0.0000, 2.0621, 2.7237)},
    {"name": 'Tail5', "parent": 'Tail4', "head": (0.0000, 2.0395, 2.4126)},
    {"name": 'Tail6', "parent": 'Tail5', "head": (0.0000, 2.0279, 2.0671)},
    {"name": 'Tail7', "parent": 'Tail6', "head": (0.0000, 2.0697, 1.6650)},
    {"name": 'PoleTargetBack.L', "parent": 'Body', "head": (0.4190, -3.7887, 0.9010)},
    {"name": 'PoleTarget.L', "parent": 'Body', "head": (0.4195, -3.2326, 0.9048)},
    {"name": 'PoleTargetBack.R', "parent": 'Body', "head": (-0.4190, -3.7887, 0.9010)},
    {"name": 'PoleTarget.R', "parent": 'Body', "head": (-0.4195, -3.2326, 0.9048)},
    {"name": 'IKBackLeg.L', "parent": None, "head": (0.4190, 1.8232, 0.3936)},
    {"name": 'FFB.L', "parent": 'IKBackLeg.L', "head": (0.4190, 1.7244, 0.1432)},
    {"name": 'IKFrontLeg.L', "parent": None, "head": (0.4195, -1.3129, 0.3936)},
    {"name": 'FF.L', "parent": 'IKFrontLeg.L', "head": (0.4195, -1.4117, 0.1432)},
    {"name": 'IKBackLeg.R', "parent": None, "head": (-0.4190, 1.8232, 0.3936)},
    {"name": 'FFB.R', "parent": 'IKBackLeg.R', "head": (-0.4190, 1.7244, 0.1432)},
    {"name": 'IKFrontLeg.R', "parent": None, "head": (-0.4195, -1.3129, 0.3936)},
    {"name": 'FF.R', "parent": 'IKFrontLeg.R', "head": (-0.4195, -1.4117, 0.1432)},
]


def ensure_object_mode():
    if bpy.context.object and getattr(bpy.context.object, "mode", "OBJECT") != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    layer = bpy.context.view_layer.layer_collection

    def find(lc):
        if lc.collection == col:
            return lc
        for child in lc.children:
            hit = find(child)
            if hit:
                return hit
        return None

    found = find(layer)
    if found:
        bpy.context.view_layer.active_layer_collection = found
    return col


def link_only(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    if obj.name not in col.objects:
        col.objects.link(obj)


def flat_mat(name, rgba):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 1.0
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = 1.0
    mat.diffuse_color = rgba
    return mat


def add_bbox_cube(slot, collection):
    loc = slot["centroid"]
    size = slot["size"]
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = slot["name"]
    obj.data.name = slot["name"]
    obj.scale = (max(size[0], 0.02), max(size[1], 0.02), max(size[2], 0.02))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in obj.data.polygons:
        p.use_smooth = False
    mat = flat_mat("Mat_" + slot["name"], slot["rgba"])
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    link_only(obj, collection)
    return obj


def origin_world_zero(obj):
    mw = obj.matrix_world.copy()
    obj.data.transform(mw)
    obj.matrix_world.identity()
    obj.location = (0.0, 0.0, 0.0)


def make_armature(collection):
    children = {}
    for b in BONES:
        children.setdefault(b["parent"], []).append(b)
    arm = bpy.data.armatures.new(ARM_NAME + "Data")
    obj = bpy.data.objects.new(ARM_NAME, arm)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    created = {}
    for b in BONES:
        eb = arm.edit_bones.new(b["name"])
        head = Vector(b["head"])
        kids = children.get(b["name"], [])
        if kids:
            tail = Vector(kids[0]["head"])
            if (tail - head).length < 0.08:
                tail = head + Vector((0.0, 0.0, 0.20))
        else:
            tail = head + Vector((0.0, 0.0, 0.25))
        eb.head = head
        eb.tail = tail
        created[b["name"]] = eb
    for b in BONES:
        parent = b["parent"]
        if parent and parent in created:
            created[b["name"]].parent = created[parent]
            created[b["name"]].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def build():
    ensure_object_mode()
    col = ensure_collection(COLLECTION)
    parts = [add_bbox_cube(slot, col) for slot in SLOTS]
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    mesh_obj = bpy.context.active_object
    mesh_obj.name = MESH_NAME
    mesh_obj.data.name = MESH_NAME
    for p in mesh_obj.data.polygons:
        p.use_smooth = False
    origin_world_zero(mesh_obj)
    link_only(mesh_obj, col)
    arm = make_armature(col)
    mesh_obj.parent = arm
    print({
        "ok": True,
        "name": mesh_obj.name,
        "verts": len(mesh_obj.data.vertices),
        "faces": len(mesh_obj.data.polygons),
        "materials": len(mesh_obj.data.materials),
        "source_tris": SOURCE_TRIS,
        "tier": TIER,
    })
    return mesh_obj


build()
