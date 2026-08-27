# bpy recipes for Blender MCP

Each block is one `execute_blender_code` payload. Copy, rename, tweak numbers.

## Scene snapshot

```python
import bpy
objs = []
for o in bpy.context.scene.objects:
    mesh = o.type == "MESH"
    objs.append({
        "name": o.name,
        "type": o.type,
        "loc": list(o.location),
        "verts": len(o.data.vertices) if mesh else 0,
        "faces": len(o.data.polygons) if mesh else 0,
    })
print({"scene": bpy.context.scene.name, "objects": objs})
```

## Ensure collection

```python
import bpy
name = "COL_Rails"
col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
if col.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col)
print({"collection": col.name})
```

## Primitive + rename + link

```python
import bpy
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
obj = bpy.context.active_object
obj.name = "SM_Rail_Post_01"
obj.data.name = "SM_Rail_Post_01"
print({"name": obj.name, "verts": len(obj.data.vertices)})
```

## Shade flat + flat color material

```python
import bpy

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

obj = bpy.data.objects["SM_Rail_Post_01"]
obj.data.materials.clear()
obj.data.materials.append(flat_mat("M_OliveRail", (0.35, 0.40, 0.22, 1.0)))
for poly in obj.data.polygons:
    poly.use_smooth = False
print({"object": obj.name, "mat": obj.data.materials[0].name})
```

## Origin to bottom (3D cursor)

```python
import bpy
from mathutils import Vector
obj = bpy.data.objects["SM_Rail_Post_01"]
ws = [obj.matrix_world @ v.co for v in obj.data.vertices]
bottom = Vector((sum(v.x for v in ws) / len(ws), sum(v.y for v in ws) / len(ws), min(v.z for v in ws)))
bpy.context.scene.cursor.location = bottom
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
print({"origin_world": list(obj.location)})
```

## Apply rotation/scale

```python
import bpy
obj = bpy.data.objects["SM_Rail_Post_01"]
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
print({"scale": list(obj.scale), "rotation": list(obj.rotation_euler)})
```

## Mirror modifier

```python
import bpy
obj = bpy.data.objects["SM_Horse_Body_01"]
mod = obj.modifiers.get("Mirror") or obj.modifiers.new("Mirror", "MIRROR")
mod.use_axis[0] = True
mod.use_clip = True
print({"modifiers": [m.name for m in obj.modifiers]})
```

## Array along Y (fence run)

```python
import bpy
obj = bpy.data.objects["SM_Rail_Straight_01"]
mod = obj.modifiers.get("Array") or obj.modifiers.new("Array", "ARRAY")
mod.count = 8
mod.use_relative_offset = True
mod.relative_offset_displace = (0.0, 1.0, 0.0)
print({"count": mod.count})
```

## Export selected GLB

```python
import bpy
path = "/tmp/SM_Rail_Straight_01.glb"
bpy.ops.object.select_all(action="DESELECT")
obj = bpy.data.objects["SM_Rail_Straight_01"]
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(filepath=path, use_selection=True, export_format="GLB")
print({"ok": True, "path": path, "verts": len(obj.data.vertices), "faces": len(obj.data.polygons)})
```

## Export selected FBX

```python
import bpy
path = "/tmp/SM_Rail_Straight_01.fbx"
obj = bpy.data.objects["SM_Rail_Straight_01"]
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_scale_options="FBX_SCALE_ALL")
print({"ok": True, "path": path})
```

## Palette (Grand Sire muted)

| Role | RGBA |
|---|---|
| Olive rail | `(0.35, 0.40, 0.22, 1)` |
| Off-white board | `(0.86, 0.84, 0.78, 1)` |
| Dirt tan | `(0.45, 0.34, 0.22, 1)` |
| Dusty rose | `(0.72, 0.48, 0.48, 1)` |
| Cream flower | `(0.93, 0.86, 0.62, 1)` |
| Pale grey | `(0.72, 0.72, 0.70, 1)` |
