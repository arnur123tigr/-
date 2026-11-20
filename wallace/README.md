# wallace — «Невидимая стена между Бали и Ломбоком» / «Бали мен Ломбок арасындағы көрінбейтін қабырға» (KZ + RU)
GEO-KARTA reel (script 8 of the 20.11.2026 batch), JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield). 10 scenes.

- Engine: 2D canvas over NASA Blue Marble (from `brazil/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Textures: `prep_tex.py` (Blue Marble tiles D1, D2 from assets.science.nasa.gov into /home/user/data) + `grade.py` -> `tex/ind.jpg` (Indonesia–Australia, 30 px/deg),
  `tex/mid.jpg` (Sunda/Wallacea, 80 px/deg), `tex/bl.jpg` (Bali–Lombok, 240 px/deg); `tex/world.jpg` from earlier reels.
- Ice-age land bridges: `prep_shelf.py` reads Mapzen/AWS Terrarium elevation tiles (zoom 6) and writes `tex/shelf_20..120.png` (sea floor shallower than d m as dry land).
  With −120 m the Sunda shelf joins Java and Bali to Asia, while the Lombok Strait (sill > 250 m) stays water.
- `prep_shapes.py` (Natural Earth 10m) -> `shapes.json`: land west / east of a schematic Wallace line, Bali and Lombok outlines, borders.
- Animals are Noto Color Emoji drawn without canvas shadow (with a shadow SwiftShader draws only the shadow). Wallace portrait is drawn in code. Cutaway profile is schematic.
- Voice: ElevenLabs eleven_v4, one take each: RU Egor energetic (g1G73EpCIdK4HUyDiLYF), KZ Ерсұлтан (Wa1HorICOC58Tie62cWB).
  `python3 words.py vo_<l>.mp3 words_<l>.json <ru|kk> medium` -> `find_beats.py` -> `raw_beats.json` -> `beats.py` -> `beats.json`, `caps_<l>.json`.
- Build: `./build.sh ru|kk` -> `out/wallace_<lang>.mp4` (with music only). Corner logo 122 px.
- Facts: Britannica (Wallace Line), NHM London, Sundaland (−120 m), Lombok Strait (250+ m). Bali–Lombok ≈ 35 km between the main islands.
