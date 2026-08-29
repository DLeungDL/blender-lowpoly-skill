# 低模怎麼做

搭配 `SKILL.zh-Hant.md`。每段 bpy 都是一次 `execute_blender_code`（或腳本裡的一節）。複製、改名、改數字。

要打到的樣子：看得見的切面、Shade Flat、1–4 個單色、沒有圖片貼圖。完成前截四視圖（front、side、3/4、top）。

## 共用

### 作用中物件：Shade Flat + 平面色

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

### 原點移到接地（世界座標 Z 最小）

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

## 做法 A — 組件（方塊 + Array）

不要 bevel。不要 subdivide。不要抖動頂點。一個方塊一個零件。

### 欄杆（橫樑 + 斜柱）

1. 方塊拉成長扁橫樑（米白）。
2. 方塊拉成柱（深綠）。沿橫樑 Array。
3. 柱在樑下面。X 向微微外傾可以，不要彎。
4. 樑比頭尾兩柱略長一點。
5. 兩個材質。原點放在第一根柱落地處（模組）或拼貼起點。

### 看台

1. 先擋 **側視輪廓**（階梯、可有挑空），再擠出寬度。
2. 人潮不是角色。一個人 = 身體方塊 + 頭方塊（8–20 tris）。
3. 每排 Array。3–5 個土色材質，套用後隨機指定。
4. 前緣底下用綠色基座方塊。
5. 只用直角和簡單斜面。

不要把座位做成一張張椅子。凹進去的深色板加上一排排方塊人就夠。

---

## 做法 B — 稜面有機

一開始就要低面。用大面長體積。Shade Flat 就是著色器。

### 層疊松樹

1. 樹幹：8 邊圓柱，微收尖，中棕。原點在根。
2. 樹冠：**三層由下而上收尖的體積**，底最大、頂最尖。用有面的圓錐／壓扁的 icosphere／拉過角的方塊，不要光滑球。
3. 每層微轉或微縮，讓俯視是不規則套疊多邊形，不是正圓。
4. 兩個材質：樹葉灰綠、樹幹棕。
5. 側視 = 階梯三角形。俯視 = 一圈套一圈。

### 綠籬／切面塊

1. 方塊拉成長塊。
2. 切幾刀讓輪廓用**切面**變圓（小 bevel 或一次 subdivide，再三角化）。
3. 可把頂點輕輕挪一下，讓邊不規則，不要做成 CAD 圓角。
4. 一個灰綠材質。Shade Flat。三角形**就是**表面細節。
5. 不要貼青苔圖。不要粒子系統。

### 風格化四足（馬）

當**體積**做，不要當雕塑。

1. 先側視：身體盒、頸盒、頭盒、四條腿柱、鬃板、尾板。
2. 拉頂點讓側輪廓有拱頸、背凹、腿收尖。關節是**折角**，不是加迴圈線。
3. 3/4：胸和臀加寬，腰略窄（俯視要讀得出來）。
4. 耳朵 = 2–3 個三角柱。眼睛 = 一塊黑面或一個黑色材質槽。白章 = 額頭往下的白面。蹄 = 最底面改成米色材質，不要做成鞋子。
5. 鬃和尾在輪廓上是深色塊，但要**焊進同一張 mesh**。不要把四肢留成獨立物件。
6. 材質：2–3 個槽，用面指定（身體、鬃／尾、白章／蹄／眼）。不要 UV，不要圖片貼圖。
7. 對齊四視圖參考時用 Shade Flat。若部分面標 smooth 但頂點已拆開，看起來也會是切面。
8. 原點在 (0,0,0)。蹄在 Z=0（差幾公分內）。套用旋轉／縮放。

**實測農場動物 GLB**（動物做法以這包為準）。全三角、一張 mesh，可加骨架：

| 模型 | Verts | Tris | 材質槽 | Bones |
|---|---:|---:|---:|---:|
| 豬 Pig | 1158 | 562 | 2 | 24 |
| 羊 Sheep | 1262 | 610 | 2 | 24 |
| 巴哥 Pug | 1284 | 644 | 2 | 24 |
| 羊駝 Llama | 1365 | 661 | 3 | 24 |
| 馬 Horse | 1436 | 690 | 2 | 28 |
| 牛 Cow | 1644 | 796 | 3 | 28 |
| 斑馬 Zebra | 2776 | 1354 | 2 | 28 |

面數停在 **560–1400 tris**。24 骨（無尾）或 28 骨（Tail1–4）。可選動畫：Idle、Jump；完整一組再加 Walk、WalkSlow、Run、Death。

旁邊那包 **FBX** 是另一套：約 1800–2500 tris、全光滑四邊、50–70 根 IK 骨、匯入時 Principled Alpha=0。不要抄它的面數、著色或骨架。

跑步循環（只有被要求時才做）：四個命名姿勢 — `gathered`、`extended`、`airborne`、`landing`。轉整條腿。不要為變形加面。

不要：Subdivision、圖片貼圖、鼻孔空腔、一根根毛、把四肢拆成獨立物件。
---

## 顏色

單色槽，roughness 1。可當起點的 RGBA（使用者有給色或截圖就跟那份）：

| 用途 | RGBA |
|---|---|
| 樹葉／綠籬 | `(0.40, 0.46, 0.28, 1)` |
| 樹幹／深柱 | `(0.35, 0.22, 0.12, 1)` 或 `(0.18, 0.28, 0.16, 1)` |
| 米白欄杆／混凝土 | `(0.86, 0.84, 0.78, 1)` |
| 馬身 | `(0.45, 0.28, 0.16, 1)` |
| 鬃 | `(0.12, 0.08, 0.06, 1)` |
| 白章 | `(0.92, 0.90, 0.86, 1)` |
| 人潮土色 | 灰、棕、悶褐 |

## 匯出

只選該資產。原點已在地面或拼貼鉸鏈。套用旋轉和縮放（`location=False`）。Shade Flat。法線朝外。匯出選取 GLB。回傳 `{ok, path, name, verts, faces, materials}`。
