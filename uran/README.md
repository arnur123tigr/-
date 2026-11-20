# uran — «Казахстан — урановая сверхдержава» / «Қазақстан — уран алыбы» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield). 10 scenes from Arunur's script (script 6 of the 20.11 batch).

- Engine: 2D canvas over NASA Blue Marble (from `teniz/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
  Textures `tex/world.jpg`, `tex/ca.jpg` (Central Asia 80 ppd) reused from teniz/. `prep_shapes.py` -> `shapes.json` (Natural Earth 10m countries, Syr Darya, Balkhash, Aral).
- Drawn parts: uranium provinces Шу-Сарысу and Сырдарья and the Chu river are schematic polygons/lines; in-situ leaching cutaway (`cutaway()`), coal comparison (`coalPanel()`),
  close-up of a well field = procedural grain + hex grid of wells (`wellField()`).
- Voice: ElevenLabs eleven_v4, one take each — RU Egor energetic (708 credits, 42.8 s), KZ Ерсұлтан (711 credits, 45.2 s), flow TKBeETkGXt5HUgSBjFgN.
  `python3 words.py vo_<l>.mp3 words_<l>.json <ru|kk> medium`, then `beats.py` -> `beats.json`, `caps_<l>.json`.
- Build: `./build.sh ru|kk` -> `out/uran_<lang>.mp4` (with music only). Corner logo 122 px.
- Facts (WNA): Kazakhstan ≈40 % of world uranium mining (43 % in 2022), #1 since 2009; Canada ≈15 %, Namibia ≈11 %, Australia ≈9 %;
  ISL mining in the Chu-Sarysu and Syrdarya provinces; 1 t natural uranium ≈ 16 000 t coal (≈230 rail wagons of 70 t, our addition).
