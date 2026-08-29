# How to build the low-poly look

Companion to `SKILL.md`. Each bpy block is one `execute_blender_code` payload (or one section of a script). Copy, rename, tweak numbers.

Hit this look: visible facets, Shade Flat, 1–4 solid colors, no image textures. Screenshot a four-view sheet (front, side, 3/4, top) before calling it done.

## Shared helpers

### Shade flat + flat color on the active object

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

obj = bpy.context.active_object
for poly in obj.data.polygons:
    poly.use_smooth = False
print({"object": obj.name, "flat": True})
```

### Origin to ground (world Z min)

```python
import bpy
from mathutils import Vector
obj = bpy.context.active_object
ws = [obj.matrix_world @ v.co for v in obj.data.vertices]
bottom = Vector((sum(v.x for v in ws) / len(ws), sum(v.y for v in ws) / len(ws), min(v.z for v in ws)))
bpy.context.scene.cursor.location = bottom
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
print({"origin_world": list(obj.location)})
```

---

## Language A — kit (cubes + Array)

No bevel. No subdivide. No jitter. One cube per part.

### Rail (beam + raked posts)

1. Cube scaled into a long thin beam (off-white).
2. Cube scaled into a post (dark green). Array along the beam.
3. Posts sit under the beam. A slight outward rake on X is fine; do not curve them.
4. Beam overhangs the first and last post a little.
5. Two materials. Origin at ground under the first post (modular) or at the tile start.

```python
import bpy

def cube(name, size, loc, scale):
    bpy.ops.mesh.primitive_cube_add(size=size, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in obj.data.polygons:
        p.use_smooth = False
    return obj

def flat_mat(name, rgba):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 1.0
    mat.diffuse_color = rgba
    return mat

beam = cube("Rail_Beam", 1.0, (0, 3.0, 1.05), (0.08, 3.2, 0.08))
beam.data.materials.append(flat_mat("Mat_Rail", (0.86, 0.84, 0.78, 1)))
post = cube("Rail_Post", 1.0, (0.04, 0.4, 0.5), (0.08, 0.08, 0.5))
post.rotation_euler[0] = 0.08
post.data.materials.append(flat_mat("Mat_Post", (0.18, 0.28, 0.16, 1)))
mod = post.modifiers.new("Array", "ARRAY")
mod.count = 6
mod.use_relative_offset = True
mod.relative_offset_displace = (0.0, 4.0, 0.0)
print({"beam": beam.name, "post": post.name, "count": mod.count})
```

### Stadium / grandstand

1. Block the **side-view profile** first (stepped decks, maybe an overhang). Extrude for width.
2. Crowd is not characters. One person = torso cube + head cube (8–20 tris).
3. Array the person along each row. 3–5 earth-tone materials, assigned at random per copy after apply.
4. Green base blocks under the front edge.
5. Right angles and simple slopes only.

Do not model seats as individual chairs. A recessed dark slab plus a grid of people is enough.

### Crowd person (then Array)

```python
import bpy

def cube(name, loc, scale, rgba):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in obj.data.polygons:
        p.use_smooth = False
    mat = bpy.data.materials.new(name + "_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 1.0
    obj.data.materials.append(mat)
    return obj

body = cube("Person_Body", (0, 0, 0.35), (0.18, 0.14, 0.35), (0.45, 0.42, 0.38, 1))
head = cube("Person_Head", (0, 0, 0.78), (0.12, 0.12, 0.12), (0.78, 0.62, 0.50, 1))
print({"body": body.name, "head": head.name})
```

---

## Language B — faceted organic

Start low. Add volume with planes. Shade Flat is the shader.

### Pine / stacked tree

1. Trunk: cylinder, 8 vertices, slight taper, medium brown. Origin at the base.
2. Foliage: **three stacked tapered volumes**, largest at the bottom, point at the top. Each is a faceted cone / scaled icosphere / cuboid with corners pulled in — not a smooth sphere.
3. Slightly rotate or scale each tier off-axis so the top view is nested irregular polygons, not perfect circles.
4. Two materials: foliage sage, trunk brown.
5. Side view = stepped triangle. Top view = concentric irregular rings.

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
    mat.diffuse_color = rgba
    return mat

def shade_flat(obj):
    for p in obj.data.polygons:
        p.use_smooth = False

bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.18, radius2=0.08, depth=0.8, location=(0, 0, 0.4))
trunk = bpy.context.active_object
trunk.name = "Tree_Trunk"
trunk.data.materials.append(flat_mat("Mat_Bark", (0.35, 0.22, 0.12, 1)))
shade_flat(trunk)

tiers = [(0.9, 1.1, 0.35), (0.65, 0.9, 0.28), (0.4, 0.7, 0.22)]
z = 0.95
names = []
for i, (r, depth, lift) in enumerate(tiers, 1):
    bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=r, radius2=0.05, depth=depth, location=(0, 0, z))
    leaf = bpy.context.active_object
    leaf.name = f"Tree_Foliage_{i:02d}"
    leaf.rotation_euler[2] = 0.15 * i
    leaf.data.materials.append(flat_mat("Mat_Foliage", (0.40, 0.46, 0.28, 1)))
    shade_flat(leaf)
    names.append(leaf.name)
    z += lift
print({"trunk": trunk.name, "foliage": names})
```

### Hedge / faceted block

1. Cube, scale to an oblong.
2. Inset enough cuts to round the silhouette **with facets** (a small bevel or one subdivide, then triangulate).
3. Optional: displace verts a little so edges are irregular, not a CAD fillet.
4. One sage material. Shade Flat. The triangles **are** the surface detail.
5. Do not texture moss. Do not add a particle system.

### Stylized quadruped (two tiers)

Build as **volumes**, not a sculpt. Shared for both tiers:

1. Side view first: body box, neck box, head box, four leg prisms, mane slab, tail slab.
2. Pull verts so the side silhouette has an arched neck, a dip at the back, tapered legs. Joints are **bends**, not extra loops.
3. 3/4 view: widen chest and haunches, keep the waist slightly narrower (read it from the top view).
4. Ears = 2–3 triangle prisms. Weld **everything into one mesh**. Do not leave limbs as objects.
5. No UVs, no image textures. Origin at (0,0,0). Feet on Z=0. Apply rotation/scale.
6. Shade Flat to match turnaround sheets. Split verts also read faceted if some faces are marked smooth.

Pick **compact** or **detailed** and say which. Default compact. Use detailed when the user wants Gallop / Attack / Eating, or separate colors for eyes, hooves, muzzle, and hair.

#### Compact (560–1400 tris)

2–3 material slots (body, mane/tail, blaze/hoof/eye as needed). 24 bones (no tail) or 28 (Tail1–4). Clips: Idle, Jump; larger compact set adds Walk, WalkSlow, Run, Death.

Measured compact GLBs:

| Model | Verts | Tris | Slots | Bones |
|---|---:|---:|---:|---:|
| Pig | 1158 | 562 | 2 | 24 |
| Sheep | 1262 | 610 | 2 | 24 |
| Pug | 1284 | 644 | 2 | 24 |
| Llama | 1365 | 661 | 3 | 24 |
| Horse | 1436 | 690 | 2 | 28 |
| Cow | 1644 | 796 | 3 | 28 |
| Zebra | 2776 | 1354 | 2 | 28 |

#### Detailed (1800–2500 tris)

5–8 slots, typically `Main`, `Main_Light`, `Main_Dark`, `Hair`, `Hooves`, `Muzzle`, `Eye_Black`, `Eye_White`. Eyes and hooves are extra faces on the same mesh, not separate objects. ~42–51 bones. Clips include Idle, Idle_2, Walk, Gallop, Gallop_Jump, Eating, Attack_Headbutt / Attack_Kick, Death, hit reacts.

Measured detailed GLBs (same mesh as the large FBX zip; prefer GLB):

| Model | Verts | Tris | Slots | Bones | Actions |
|---|---:|---:|---:|---:|---:|
| Fox | 3752 | 1848 | 5 | 51 | 24 |
| Horse | 4400 | 2182 | 8 | 50 | 26 |
| Cow | 4970 | 2450 | 7 | 42 | 25 |

The FBX of this pack is the same topology with a worse import (all-smooth quads, Principled Alpha=0, extra IK bones). If both files exist, open the GLB.

Gallop holds if the user wants a sheet not a clip: `gathered`, `extended`, `airborne`, `landing`. Rotate whole-limb bones. Do not add topology for deformation.

Do not: Subdivision, image textures, nostril cavities, individual hairs, separate limb objects.
---

## Color

Solid slots, roughness 1. Example starting RGBA (linear-ish, tweak in viewport):

| Role | RGBA |
|---|---|
| Sage foliage / hedge | `(0.40, 0.46, 0.28, 1)` |
| Bark / dark post | `(0.35, 0.22, 0.12, 1)` or `(0.18, 0.28, 0.16, 1)` |
| Off-white rail / concrete | `(0.86, 0.84, 0.78, 1)` |
| Horse body | `(0.45, 0.28, 0.16, 1)` |
| Mane | `(0.12, 0.08, 0.06, 1)` |
| Blaze | `(0.92, 0.90, 0.86, 1)` |
| Crowd earth tones | greys, tans, muted browns |

These are starting points, not a project bible. If the user gives hex or a screenshot, match that instead.

## Export reminder

Select only the asset. Origin already at ground or tile hinge. Apply rotation and scale (`location=False`). Shade flat. Recalculate normals outward. Export selected GLB. Return `{ok, path, name, verts, faces, materials}`.
