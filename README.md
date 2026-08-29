English · [繁體中文](README.zh-Hant.md)

# blender-mcp-skill

A simple LLM skill for making **low-poly** assets in Blender.

Two paths:

1. **Blender MCP** if the agent has live MCP tools.
2. A self-contained **bpy script** if it does not.

This is a generic guidebook. It does not bind naming, palette, or project style.

## Layout

```
SKILL.md
SKILL.zh-Hant.md
README.zh-Hant.md
references/lowpoly-build.md
references/lowpoly-build.zh-Hant.md
references/bpy-recipes.md
references/agent-protocol.md
```

Copy the folder as `skills/blender-lowpoly/` into your agent.

## What it encodes

- Pick MCP or bpy, not both in one step
- Two build languages: kit (cubes + Array) or faceted organic
- Four-view check (front, side, 3/4, top)
- Inspect → blockout → check → shade flat + color slots → export
- Low-poly, hard-edge, Shade Flat, no image textures
- Use the names the user gave
- Safety: no quit, no home-file wipe, no remote Python

## MCP config (example)

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

Align host/port with the BlenderMCP panel. Start the server in Blender before the agent runs.

## License

Use and modify for your own agents. Not affiliated with the Blender Foundation.
