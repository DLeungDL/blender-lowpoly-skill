---
name: blender-mcp
description: Drive a live Blender session through Blender MCP for an AI agent. Use when modeling, editing, inspecting, rendering, or exporting in Blender via MCP tools or bpy, including low-poly game assets, viewport screenshots, and Grand Sire / 馬王 style props.
metadata:
  version: "1.1.0"
  type: workflow
  mcp: blender-mcp
---

# blender-mcp

Operate the user's live Blender through MCP. Inspect first. Mutate in small bpy chunks. Screenshot after visual changes. Never invent scene state.

This skill is for an **AI agent** (OpenClaw / Grok Bot / compatible). The agent does not "know" the .blend — only what tools return.

## Connection check (first action every session)

1. List live MCP tools. Expect some of `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code` or `execute_code`. Forks may prefix `bm_`.
2. Call `get_scene_info`. If it fails, stop. Tell the user in Traditional Chinese
   - 開啟 Blender（Blender）
   - 啟用 addon **Interface: Blender MCP**
   - 視窗 `N` → **BlenderMCP** → **Start MCP Server**（預設 `localhost:9876`）
   - 同一個 socket 只連一個 MCP client
3. Optional screenshot before the first edit.

Default — `BLENDER_HOST=localhost`, `BLENDER_PORT=9876`.

Do not keep retrying a dead socket. One clear connect instruction is enough.

## Tool policy

| Prefer | When |
|---|---|
| `get_scene_info` | Start of every task; after big edits |
| `get_object_info` | One named object |
| `get_viewport_screenshot` | After each meaningful visual change |
| Structured tools (`create_object`, `modify_object`, …) | Only if the live server exposes them |
| `execute_blender_code` / `execute_code` | Everything else |

### Rules for execute snippets

- One intent per call (create mesh; then material; then origin; then export).
- Self-contained. Always `import bpy`. Do not reuse locals from a previous call.
- Return a short dict / print summary (names, counts, paths). Never dump vertex arrays.
- After `bpy.ops` that enter Edit Mode, return to Object Mode in the same snippet.
- Set `obj.select_set(True)` and `bpy.context.view_layer.objects.active = obj` before object ops.
- Never `bpy.ops.wm.quit_blender()`.
- Never `read_homefile`, wipe collections, or delete unnamed user work without asking.
- Never fetch remote Python. Never read credentials from disk.

If a call errors, read the traceback, fix that snippet only, retry once or twice. Then report.

Full recipes — [references/bpy-recipes.md](references/bpy-recipes.md)

Agent handshake and tool-name aliases — [references/agent-protocol.md](references/agent-protocol.md)

## Modeling loop

```
get_scene_info
  → plan names, poly budget, origin, units
  → execute (blockout)
  → screenshot
  → execute (refine / shade flat / materials)
  → screenshot
  → execute (origin, apply rotation+scale, export)
  → get_scene_info + screenshot
```

Names — `SM_<Thing>_<Variant>` (example `SM_Rail_Straight_01`).
Collections — `COL_<Group>` (example `COL_Rails`).
Materials — `M_<ColorRole>` (example `M_OliveRail`).

## Default art direction (low-poly game assets)

Apply unless the user overrides.

- Low-poly, hard-edge, **Shade Flat**. No Auto Smooth unless asked.
- Quads while modeling. Triangulate only at export if the engine needs it.
- Geometry carries the silhouette. No extra loops on flat planes.
- No PBR stack by default. Flat Principled or Emission, or vertex colors.
- Muted Grand Sire / 馬王 palette when building track props — olive rails, off-white boards, dirt-tan ground, dusty rose / cream accents.
- Poly budget — small prop 300–1500 tris; hero prop 2–5k; stylized horse 3–8k.
- Origin at ground contact or hinge.
- Units metric, scale 1.0 unless the open file already differs.
- Export **glTF/GLB** or **FBX**. Report the absolute path.

Palette RGBA is in [references/bpy-recipes.md](references/bpy-recipes.md).

## Export checklist (one snippet)

1. Select only the target object(s).
2. Origin already correct.
3. Apply rotation and scale (`location=False`).
4. Shade flat. Recalculate normals outward.
5. Export selected to the path the user gave (else next to the .blend or `/tmp`).
6. Return `{ok, path, name, verts, faces, materials}`.

Apply live modifiers before export if the engine will not evaluate them.

## Safety

- `execute_blender_code` is arbitrary Python inside the user's Blender.
- Poly Haven / Sketchfab / Rodin / Hunyuan are optional. Use only when the user wants external assets. Prefer hand-built low-poly for this style.

## Report back (every completed task)

List in Traditional Chinese with bilingual key terms

- 建立或修改的物件（objects）
- Collection 名稱
- 約略 verts / faces
- 材質名稱與顏色
- 匯出路徑（export path）若有
- 最後一張 viewport screenshot 看到什麼（輪廓 / 明顯錯誤）
- 下一步建議（一句）
