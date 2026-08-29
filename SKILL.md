---
name: blender-lowpoly
description: Use this when making low-poly assets in Blender, either through Blender MCP or by writing a bpy script.
metadata:
  version: "2.0.0"
  type: workflow
---

English · [繁體中文](SKILL.zh-Hant.md)

# blender-lowpoly

Guidebook for an LLM making **low-poly** game assets in a live or scripted Blender session.

## Path

1. If Blender MCP tools are available (`get_scene_info`, `execute_blender_code` / `execute_code`, viewport screenshot): use MCP.
2. Otherwise write a self-contained `bpy` script the user can run in Blender (Scripting workspace or `blender --python`).

Do not mix the two in one step. Say which path you are using.

## Loop

```
inspect scene
  → plan names, poly budget, origin, units
  → small edit (one intent)
  → check (screenshot or printed counts)
  → export
```

Never invent scene state. Only trust tool output or script prints.

## Defaults (unless the user overrides)

- Low-poly, hard edges, **Shade Flat**. No Auto Smooth.
- Quads while modeling. Triangulate only at export if the engine needs it.
- Silhouette from geometry. No extra loops on flat planes.
- Flat color materials (Principled or Emission). No PBR stack.
- Origin at ground contact or hinge.
- Metric units, scale 1.0 unless the open file already differs.
- Export **selected** as glTF/GLB (FBX only if asked). Report the absolute path.
- Poly budget unless specified: small prop 300–1500 tris, hero prop 2–5k.

## Naming

Use the names the user gave. If none, pick clear English names and say what you picked. Do not invent a project prefix (`SM_`, `COL_`, …) unless they asked for one.

## MCP rules

- First action every session: list live tools, then `get_scene_info`.
- If connect fails, stop. Tell the user to: open Blender → enable addon **Interface: Blender MCP** → `N` panel → **Start MCP Server** (default `localhost:9876`) → one MCP client only.
- One intent per `execute_*` call. Always `import bpy`. Do not reuse locals from a previous call.
- Return a short dict (names, counts, paths). Never dump vertex arrays.
- After Edit Mode ops, return to Object Mode in the same snippet.
- Set the object selected and active before object ops.
- Screenshot after each meaningful visual change.
- Tool names vary by fork (`bm_` prefix, `execute_code`, …). Bind by capability, not exact string.

## bpy script rules

- One self-contained file. Same safety and return-summary rules as MCP snippets.
- Print a short dict at the end: `{ok, names, verts, faces, path}`.
- No modal operators. Keep runtime to a few seconds unless the user asked for a render.

## Safety

- Never `bpy.ops.wm.quit_blender()`.
- Never `read_homefile`, wipe collections, or delete unnamed user work without asking.
- Never fetch remote Python. Never read credentials from disk.

## Report back

- Objects created or changed
- Approx verts / faces
- Material names and colors
- Export path if any
- What the last screenshot or print shows
- One next-step suggestion
