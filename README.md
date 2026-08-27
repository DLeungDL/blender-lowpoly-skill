# blender-mcp-skill

AI agent skill for driving a **live Blender** session through **Blender MCP**.

Target agents: OpenClaw, Grok Bot, or any MCP client that can load `SKILL.md`.

## Layout

```
SKILL.md
references/bpy-recipes.md
references/agent-protocol.md
```

Copy the folder as `skills/blender-mcp/` into your agent.

## What it encodes

- Connection check (`localhost:9876`, one MCP client)
- Inspect → small `bpy` chunks → viewport screenshot → export
- Low-poly, hard-edge, Shade Flat defaults
- Naming: `SM_`, `COL_`, `M_`
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
