# Low-poly animal reference scripts

Self-contained `bpy` reconstructions of the Quaternius compact (`refs/glb/`) and
detailed (`refs/glb2/`) animals. **Calibrated to the GLBs, not 1:1 vertex clones.**

Each script builds named cubes / 8-gon cylinders / cones at measured bone heads
and material-island colours / bboxes, Shade Flat, then joins + welds into one
mesh. Origin is world `(0,0,0)` with feet on `Z=0`. An armature is created with
the **real bone names** from the GLB (positions from measured heads; no clips).

Measurements: `_extracted.json` (all 12 inspected GLBs).

## How to run

In Blender Scripting, open a file and Run Script. Or:

```bash
blender --python horse_compact.py
```

Headless (this box):

```bash
/home/box/.local/bin/blender --background --python horse_compact.py
```

Rerun is safe: the script deletes only the collection it creates
(`REF_Horse_Compact`, `REF_Cow_Detailed`, …). It does not wipe the rest of the
scene, reload a home file, or quit Blender.

Each script prints `{ok, name, verts, faces, materials, path_note}`.

## Compact vs detailed

| Tier | Source folder | Tris (measured) | Slots | Bones | Clips |
|---|---|---|---|---|---|
| **Compact** | `refs/glb/` | 560–1400 | 2–3 | 24 or 28 | Idle / Jump; larger set adds Walk / Run / Death |
| **Detailed** | `refs/glb2/` | 1800–2500 | 5–8 | ~42–51 | Gallop, Eating, Attack, extra Idles |

Compact is the default style target for the low-poly pack (blocky Mix-B slots).
Detailed GLBs split Main / Main_Light / Hair / Hooves / Muzzle / Eyes.

## Scripts

### Compact (`refs/glb/`)

| Script | GLB | Verts | Tris | Slots | Bones | Collection |
|---|---|---:|---:|---:|---:|---|
| `horse_compact.py` | Horse.glb | 1436 | 690 | 2 | 28 | `REF_Horse_Compact` |
| `cow_compact.py` | Cow.glb | 1644 | 796 | 3 | 28 | `REF_Cow_Compact` |
| `pig_compact.py` | Pig.glb | 1158 | 562 | 2 | 24 | `REF_Pig_Compact` |
| `sheep_compact.py` | Sheep.glb | 1262 | 610 | 2 | 24 | `REF_Sheep_Compact` |

### Detailed (`refs/glb2/`)

| Script | GLB | Verts | Tris | Slots | Bones | Collection |
|---|---|---:|---:|---:|---:|---|
| `horse_detailed.py` | Horse.glb | 4400 | 2182 | 8 | 50 | `REF_Horse_Detailed` |
| `cow_detailed.py` | Cow.glb | 4970 | 2450 | 7 | 42 | `REF_Cow_Detailed` |
| `fox_detailed.py` | Fox.glb | 3752 | 1848 | 5 | 51 | `REF_Fox_Detailed` |
| `white_horse_detailed.py` | White Horse.glb | 4400 | 2182 | 7 | 50 | `REF_WhiteHorse_Detailed` |
| `wolf_detailed.py` | Wolf.glb | 3994 | 1962 | 4 | 51 | `REF_Wolf_Detailed` |

Also inspected (no reconstruction script): compact Llama, Pug, Zebra.

## Notes

- **Sheep compact** source mesh origin is mid-body (`feet_z = -3.511`). The
  script shifts so feet sit on Z=0. Its armature imported Y-up / unconverted;
  bone *names* are preserved at measured heads.
- Compact horse body colour is Mix RGB B `(0.140, 0.059, 0.037)`; dark slot
  `(0.016, 0.016, 0.016)` is mane / tail / hooves / blaze.
- Detailed horse adds localized islands: Main_Light blaze, Main_Dark face,
  Muzzle, Hooves, Eye_Black, Eye_White — placed at measured centroids/bboxes.
- Do not dump raw vertex arrays from the GLB into these scripts. Tweak the
  primitive sizes if a silhouette is off.
