---
name: blender-lowpoly
description: 在 Blender 裡做低模（low-poly）資產時使用，可走 Blender MCP 或撰寫 bpy 腳本（script）。
metadata:
  version: "2.0.0"
  type: workflow
  locale: zh-Hant
---

繁體中文 · [English](SKILL.md)

# blender-lowpoly

給 LLM 的指南：在即時或腳本化的 Blender 工作階段裡，製作低模（low-poly）遊戲資產。

## 路徑（path）

1. 若有 Blender MCP 工具（`get_scene_info`、`execute_blender_code` / `execute_code`、viewport 截圖）：走 MCP。
2. 否則寫一份可獨立執行的 `bpy` 腳本，讓使用者在 Blender 裡跑（Scripting 工作區，或 `blender --python`）。

同一步不要混用兩條路。要說你正在用哪一條。

## 迴圈（loop）

```
檢查場景（inspect）
  → 規劃名稱、面數預算（poly budget）、原點（origin）、單位
  → 小改（一次一個意圖）
  → 核對（截圖或印出數量）
  → 匯出（export）
```

不要捏造場景狀態。只相信工具回傳或腳本 print。

## 預設（除非使用者另指定）

- 低模、硬邊（hard-edge）、**Shade Flat**。不要 Auto Smooth。
- 建模用四邊形（quads）。只有引擎需要時，才在匯出時三角化（triangulate）。
- 輪廓靠幾何本身。平面不要加多餘迴圈（loop）。
- 平面色材質（Principled 或 Emission）。不要 PBR 堆疊。
- 原點（origin）放在接地處或鉸鏈。
- 公制單位，縮放 1.0（開著的檔案若已不同則跟隨檔案）。
- 只匯出**選取物**為 glTF/GLB（有要求才用 FBX）。回報絕對路徑。
- 未指定面數時：小道具 300–1500 tris，主角級道具 2–5k。

## 命名（naming）

用使用者給的名稱。沒給就選清楚的英文名，並說你選了什麼。不要自創專案前綴（`SM_`、`COL_` 等），除非使用者要求。

## MCP 規則

- 每次工作階段的第一個動作：列出即時工具，然後呼叫 `get_scene_info`。
- 連線失敗就停。告訴使用者：開啟 Blender → 啟用外掛 **Interface: Blender MCP** → `N` 面板 → **Start MCP Server**（預設 `localhost:9876`）→ 同一個 socket 只連一個 MCP client。
- 每次 `execute_*` 只做一個意圖。一律 `import bpy`。不要沿用上一次呼叫的區域變數。
- 回傳短 dict（名稱、數量、路徑）。不要傾印頂點陣列。
- Edit Mode 操作結束後，同一段程式回到 Object Mode。
- 物件操作前，先設為選取且為作用中物件（active object）。
- 每次有意義的視覺變更後截圖。
- 不同 fork 的工具名稱可能不同（`bm_` 前綴、`execute_code` 等）。依能力對應，不要死記字串。

## bpy 腳本規則

- 一份可獨立執行的檔案。安全與回傳摘要規則與 MCP 片段相同。
- 結尾 print 短 dict：`{ok, names, verts, faces, path}`。
- 不要用 modal operator。執行時間控制在幾秒內，除非使用者要求渲染（render）。

## 安全（safety）

- 禁止 `bpy.ops.wm.quit_blender()`。
- 禁止 `read_homefile`、清空 collection，或未經詢問刪掉未命名的使用者作業。
- 禁止從遠端抓 Python。禁止從磁碟讀取憑證（credentials）。

## 回報

- 建立或修改的物件（objects）
- 約略 verts / faces
- 材質（material）名稱與顏色
- 若有匯出，寫出路徑（export path）
- 最後一張截圖或 print 看到什麼
- 下一步建議（一句）
