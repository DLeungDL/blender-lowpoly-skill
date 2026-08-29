繁體中文 · [English](README.md)

# blender-mcp-skill

給 LLM 用的簡易技能（skill）：在 Blender 裡做低模（low-poly）資產。

兩條路：

1. 若 agent 有即時的 MCP 工具，走 **Blender MCP**。
2. 若沒有，寫一份可獨立執行的 **bpy 腳本**（bpy script）。

這是通用指南，不綁命名規則、色盤或任何專案風格。

## 檔案結構（layout）

```
SKILL.md
SKILL.zh-Hant.md
README.zh-Hant.md
references/lowpoly-build.md
references/lowpoly-build.zh-Hant.md
references/bpy-recipes.md
references/agent-protocol.md
```

把資料夾複製成 agent 裡的 `skills/blender-lowpoly/`。

中文技能正文見 [SKILL.zh-Hant.md](SKILL.zh-Hant.md)。英文技能正文見 [SKILL.md](SKILL.md)。

## 它規定了什麼

- 一次只走 MCP 或 bpy，不要混用
- 兩種做法：組件（kit，方塊 + Array）或稜面有機（faceted organic）
- 四視圖檢查（front、side、3/4、top）
- 先檢查 → 擋形 → 核對 → Shade Flat 分件上色 → 匯出
- 預設：低模、硬邊、Shade Flat、沒有圖片貼圖
- 名稱跟使用者說的走
- 安全：不准退出 Blender、不准清掉未存場景、不准從遠端抓 Python

## MCP 設定（範例）

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

主機（host）與連接埠（port）要和 BlenderMCP 面板一致。agent 動手之前，先在 Blender 裡啟動伺服器（server）。

## 授權（license）

可自行使用與修改。與 Blender Foundation 無關。
