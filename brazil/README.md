# brazil — «Почему в Бразилии говорят по-португальски» / «Неге Бразилияда португалша сөйлейді» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield). 9 scenes from Arunur's script.

- Engine: 2D canvas over NASA Blue Marble (from `aral/` / `nemo/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Data: `prep_tex.py` (tiles B1, B2, C1 from assets.science.nasa.gov into /home/user/data) + `grade.py` -> `tex/sa.jpg` (South America), `tex/nebr.jpg`
  (Brazil's eastern bulge, 100 px/deg), `tex/ib.jpg` (Iberia); `tex/world.jpg` from aral/. `prep_shapes.py` -> `shapes.json` (Natural Earth 10m).
- Tordesillas line drawn at 46.6° W (370 leagues west of Cape Verde, the usual estimate). Voyage routes are schematic.
- Voice: `tts.py` = free Microsoft draft (edge-tts, words from WordBoundary); final = ElevenLabs Egor (RU) / Ерсұлтан (KZ),
  then `python3 words.py vo_<l>.mp3 words_<l>.json <ru|kk> medium`. Beats: `find_beats.py .` -> `raw_beats.json`; `beats.py` -> `beats.json`, `caps_<l>.json`.
- Build: `./build.sh ru|kk` -> `out/brazil_<lang>.mp4` (with music only). Corner logo 122 px.
- Facts: Britannica (Treaty of Tordesillas 1494; Cabral 1500), IBGE (~212 mln), INE Portugal (~10.6 mln).
