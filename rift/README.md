# rift — «Африка екіге бөлініп жатыр» / «Африка раскалывается надвое» (KZ + RU)
Geo batch 26.11.2026, script 3: the East African Rift (Nubian and Somali plates, magma and the valley, the Mai Mahiu road crack in Kenya 2018,
the 60 km Dabbahu fissure in Afar 2005, plates move a few mm a year, a future ocean, the Red Sea as a baby ocean, ҰБТ: divergent boundary).
GEO-KARTA script, code only (no Higgsfield). JAS EDUCATION brand, dark satellite globe, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `tyn/` (<- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `fetch_data.sh` + `prep_map.py`: `tex/main.jpg` Africa lon -20..60 lat -36..40 40 px/deg, `tex/detail.jpg` rift lon 28..50 lat -12..18
  120 px/deg (NASA Blue Marble NG B1 B2 C1 C2 + Mapzen Terrarium relief), `dem.bin`; `tex/world.jpg` from tyn/. `shapes.json`: Natural Earth borders,
  Kazakhstan, roads near Mai Mahiu; PB2002 plates (Peter Bird 2002, via fraxen/tectonicplates, ODC-By); rift branches hand-drawn (schematic).
  Kazakhstan is laid along the rift at true size, turned 90° (its west -> east runs north -> south). The future ocean is a sketch.
- Voice: «Arnur» (eleven_v4, one take per language). `prep_vo.py` shortens pauses; KZ: `SLOT=53.13,53.92 python3 prep_vo.py kk`
  splices the approved «ҰБТ-да» clip. `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py`, `mix.py`. Build: `./build.sh kk|ru` -> `rift_<lang>.mp4`.
