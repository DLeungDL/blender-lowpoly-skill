---
name: blender-lowpoly
description: 在 Blender 裡做低模（low-poly）資產時使用，可走 Blender MCP 或撰寫 bpy 腳本（script）。
metadata:
  version: "2.1.0"
  type: workflow
  locale: zh-Hant
---

繁體中文 · [English](SKILL.md)

# blender-lowpoly

給 LLM 的指南：在即時或腳本化的 Blender 工作階段裡，製作低模（low-poly）遊戲資產。

要打到的樣子：**看得見的切面、Shade Flat、單色材質、沒有 PBR 貼圖**。從基本體（primitive）堆。用四視圖檢查（front、side、3/4、top）。

## 路徑（path）

1. 若有 Blender MCP 工具（`get_scene_info`、`execute_blender_code` / `execute_code`、viewport 截圖）：走 MCP。
2. 否則寫一份可獨立執行的 `bpy` 腳本，讓使用者在 Blender 裡跑（Scripting 工作區，或 `blender --python`）。

同一步不要混用兩條路。要說你正在用哪一條。

## 迴圈（loop）

```
檢查場景（inspect）
  → 選做法（組件 kit 或 稜面有機 faceted-organic）
  → 用基本體擋形（先輪廓）
  → 四視圖檢查
  → Shade Flat + 分件上色
  → 原點、套用旋轉縮放、匯出
```

不要捏造場景狀態。只相信工具回傳或腳本 print。

## 兩種做法

每個資產只選一種。同一張 mesh 不要混。

### A. 組件（kit，硬邊基本體）

方塊和圓柱，**不要 bevel**、**不要 subdivision**、**不要抖動頂點**。重複用 Array。用在欄杆、柱、看台、方塊人潮、箱子。

- 一個方塊 = 一個零件。
- 柱 / 人潮 / 重複開間：Array modifier。引擎不會算 modifier 時，才在匯出前套用。
- 2–4 個材質槽。整件上色。除非兩色在同一 mesh，才用面指定。

### B. 稜面有機（faceted organic）

大塊看得見的三角／四邊。Shade Flat，讓每面自己受光。用在樹、綠籬、石頭、風格化動物。

- 從方塊、圓錐、或 6–8 邊圓柱開始。不要先做高模再 Decimate 當第一手段。
- 先在 **側視** 拉輪廓，再在 3/4 補體積。
- 只有葉子／石頭才小幅抖動頂點。組件零件不要抖。
- 解剖靠大面和轉折角（膝蓋 = 一個折），不要加迴圈線。
- 用 **材質槽／指定面** 上色（身體、鬃、白章、蹄）。不要圖片貼圖。

做法食譜：[references/lowpoly-build.zh-Hant.md](references/lowpoly-build.zh-Hant.md)

## 四視圖檢查（必做）

擋形後、上色後，截圖或 print，讓這四個方向都清楚：

| 視圖 | 檢查什麼 |
|---|---|
| front | 對稱、寬度、顏色分割（白章、柱） |
| side | 輪廓、收尖、關節角度、挑空 |
| 3/4 | 體積、切面受光、零件沒穿模 |
| top | 佔地面積、Array 間距、樹冠層層套疊 |

如果某個視圖像另一個物體，是輪廓錯了。改頂點，不要加線。

## 預設（除非使用者另指定）

- 低模、硬邊、**Shade Flat**。不要 Auto Smooth。不要 Subdivision Surface。
- 組件用四邊形擋形。稜面有機可以是三角，那就是風格。
- 輪廓靠幾何。平面不要加多餘迴圈（loop）。
- 平面 Principled（roughness 1、metallic 0）或 Emission。不要 PBR 堆疊，不要圖片貼圖。
- 原點（origin）放在接地處，或模組拼接的鉸鏈。
- 公制單位，縮放 1.0（開著的檔案若已不同則跟隨檔案）。
- 只匯出**選取物**為 glTF/GLB（有要求才用 FBX）。回報絕對路徑。
- 未指定面數時：組件道具 20–400 tris；葉子／石頭 80–800；風格化四足 500–2500；人潮填充 8–20。

## 命名（naming）

用使用者給的名稱。沒給就選清楚的英文名，並說你選了什麼。不要自創專案前綴（`SM_`、`COL_` 等），除非使用者要求。

## MCP 規則

- 每次工作階段的第一個動作：列出即時工具，然後呼叫 `get_scene_info`。
- 連線失敗就停。告訴使用者：開啟 Blender → 啟用外掛 **Interface: Blender MCP** → `N` 面板 → **Start MCP Server**（預設 `localhost:9876`）→ 同一個 socket 只連一個 MCP client。
- 每次 `execute_*` 只做一個意圖。一律 `import bpy`。不要沿用上一次呼叫的區域變數。
- 回傳短 dict（名稱、數量、路徑）。不要傾印頂點陣列。
- Edit Mode 操作結束後，同一段程式回到 Object Mode。
- 物件操作前，先設為選取且為作用中物件（active object）。
- 每次有意義的視覺變更後截圖。最終檢查優先做四視圖。
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

- 用了哪種做法（kit 或 faceted-organic）
- 建立或修改的物件（objects）
- 約略 verts / faces
- 材質（material）名稱與顏色
- 若有匯出，寫出路徑（export path）
- 四視圖看到什麼（輪廓／明顯錯誤）
- 下一步建議（一句）
