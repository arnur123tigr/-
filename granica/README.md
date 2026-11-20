# granica — «Самая длинная сухопутная граница в мире» / «Әлемдегі ең ұзын құрлық шекарасы» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield). 10 scenes from Arunur's script.

- Engine: 2D canvas over NASA Blue Marble (from `brazil/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
  The world texture is drawn three times (wrap across ±180°) and `poleFade()` blacks out the map beyond ±80° in wide shots.
- Textures: `tex/world.jpg`, `tex/ca.jpg` (from `teniz/`), `tex/pet.jpg` = `python3 prep_tex.py tex pet 67.5 70.5 54.6 56 240` (tile C1) + `grade.py`.
- `prep_shapes.py` -> `shapes.json` (Natural Earth 10m; Kazakhstan merged with Baikonur). Shared borders = one outline ∩ the other country,
  merged and ordered west -> east: KZ–RU is one piece (49.2° E … 87.3° E), US–CA = main + Alaska.
- Street-level shot north of Petropavlovsk: `prep_osm.py` -> `osm.json` from 6 OpenStreetMap tiles (api.openstreetmap.org/api/0.6/map,
  lon 68.55–69.45, lat 54.95–55.62): roads, rivers, forests, villages, buildings, the state border (admin_level 2). Fields are procedural. © OpenStreetMap contributors, ODbL.
- Voice: ElevenLabs eleven_v4, one take each: RU Egor energetic, KZ Ерсұлтан. `python3 words.py vo_<l>.mp3 words_<l>.json <ru|kk> medium`,
  `python3 find_beats.py .` -> `raw_beats.json`, `python3 beats.py` -> `beats.json`, `caps_<l>.json`.
- Build: `./build.sh ru|kk` -> `out/granica_<lang>.mp4` (with music only). Corner logo 122 px.
- Facts: CIA World Factbook (KZ–RU 7 644 km; VO says "about 7 500"), International Boundary Commission (US–CA 8 891 km incl. 2 475 km Alaska),
  Almaty–London ≈ 5 600 km great circle, demarcation of the KZ–RU border still in progress (MFA RK / KNB, parts planned for 2026).
