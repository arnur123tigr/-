# hormuz — «33 километра, от которых зависит мировая нефть» / «Әлем мұнайы тәуелді 33 шақырым» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield). 10 scenes from Arunur's script:
Strait of Hormuz (≈33 km, Almaty–Talgar at the same scale, tankers, Iran/Oman, closure) → Tengiz → CPC pipeline to Novorossiysk (≈1500 km, ≈80 %) →
ENT: oil fields in western Kazakhstan → Bosporus at street level (≈700 m) → CTA "link in profile header".

- Engine: 2D canvas over satellite textures (from `teniz/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
  Close-up textures fade in with zoom and have feathered edges (`feather()` in scene.html).
- Textures: `prep_tex.py` (NASA Blue Marble tile C1) + `grade.py` -> `tex/me.jpg`, `tex/gulf.jpg`, `tex/ist.jpg`; `tex/world.jpg` from teniz/.
  `prep_s2.py` -> Copernicus Sentinel-2 L2A true colour mosaics (Element84 Earth Search STAC, AWS open data):
  `tex/hor.jpg` (Hormuz, 700 px/deg; then `grade.py` + `grade_s2.py` with gulf.jpg as reference: colour match + smooth sea),
  `tex/ist2.jpg`, `tex/bos.jpg` (Istanbul / Bosporus, 1200 and 6000 px/deg, water tinted to the map teal).
- `prep_shapes.py` -> `shapes.json` (Natural Earth 10m shapefile; Kazakhstan merged with Baikonur).
- Timing: `words.py` (faster-whisper medium) -> `words_<lang>.json`; `beats.py` -> `beats.json`, `caps_<lang>.json`.
- Voices: ElevenLabs eleven_v4, one take each — RU Egor energetic (`vo_ru.mp3`), KZ Ерсұлтан (`vo_kk.mp3`).
- Build: `./build.sh ru|kk` -> `out/hormuz_<lang>.mp4` (with music only). Corner logo 122 px.
- Facts (script sources): EIA World Oil Transit Chokepoints (≈20 mb/d ≈ 20 % of world consumption, narrowest ≈21 miles ≈ 33 km);
  CPC ≈1 500 km Tengiz–Novorossiysk, ≈80 % of Kazakhstan's oil exports (Reuters); Britannica, Bosporus 0.7–3.7 km.
  The CPC route and the tanker sea lanes are schematic. Almaty–Talgar ≈ 24 km straight line, drawn at the same scale as the strait.
- Imagery credits: NASA Blue Marble; contains modified Copernicus Sentinel data (2023–2024); Natural Earth.
