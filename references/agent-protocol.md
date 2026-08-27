# Agent protocol for Blender MCP

Use this when wiring an AI agent (OpenClaw, Grok Bot, or any MCP client) to a live Blender MCP server.

## What the agent must assume

- The .blend on disk is the source of truth. Tool output is the only scene memory.
- Multiple clients on `localhost:9876` will collide. One client only.
- Tool names differ by fork. Bind by capability, not by exact string.

## Capability map

Resolve live tools to these roles

| Role | Common names |
|---|---|
| Scene inspect | `get_scene_info`, `bm_get_scene_info` |
| Object inspect | `get_object_info`, `bm_get_object_info` |
| Viewport image | `get_viewport_screenshot`, `get_screenshot`, `bm_viewport_screenshot` |
| Run bpy | `execute_blender_code`, `execute_code`, `bm_execute_blender_code` |
| Optional structured create | `create_object`, `modify_object`, `delete_object` |

If inspect + execute + screenshot exist, the agent can do the full loop. Structured create tools are optional sugar.

## bpy payload contract

Every execute call

```python
import bpy
# ... mutate ...
print({"ok": True, "name": "...", "verts": 0, "faces": 0})
```

Good returns — small JSON-like dicts.
Bad returns — full `dir(obj)`, mesh coordinates, render pixels.

Timeouts — keep snippets under a few seconds. No modal operators. No `bpy.ops.render.render` of a heavy scene unless the user asked.

## Viewport screenshot use

- Before first edit (optional baseline).
- After blockout.
- After materials / shade flat.
- After export prep (origin visible in silhouette).

Describe the image in the user-facing reply. Do not claim dimensions you did not measure.

## Failure playbook

| Symptom | Action |
|---|---|
| Connection refused / timeout | Stop. Instruct Start MCP Server. |
| `Context` poll / wrong mode | Snippet must set Object Mode and active object. |
| `KeyError` object name | `get_scene_info`, then use the real name. |
| Modifier looks missing in engine | Apply modifiers in an export snippet. |
| Axes flipped in engine | Report export options used; do not silently rotate the user's scene. |
| User has unsaved work | Do not reload factory / home file. |

## OpenClaw / local agent install

Copy this skill folder into the agent's skills directory

```
skills/blender-mcp/
  SKILL.md
  references/bpy-recipes.md
  references/agent-protocol.md
```

Point the agent's MCP config at Blender

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

Exact command depends on the installed fork (`uvx blender-mcp`, `npx`, or a local `server.py`). Keep host/port aligned with the BlenderMCP panel.

## User-facing language

When this agent talks to the current user, reply in Traditional Chinese and annotate key terms in English (Low-poly, Modifier, Origin, Shade Flat, Export).
