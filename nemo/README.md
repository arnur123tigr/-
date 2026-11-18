# nemo — «Точка Немо: ближайшие люди — в космосе» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield).
Voices: ElevenLabs eleven_v4, one take each — RU Egor energetic (`vo_ru.mp3`, 39 s), KZ Ерсұлтан (`vo_kk.mp3`, 43 s).

- Engine: 2D canvas over NASA Blue Marble (from `oguz/` / `caspian/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Data: `prep_tex.py` (tiles A2, B2 from assets.science.nasa.gov into /home/user/data) + `grade.py` -> `tex/pac.jpg`; `tex/world.jpg` from oguz/; `prep_pacific.py` -> `tex/pacmask.png` (Pacific glow for the ЕНТ/ҰБТ scene).
- Scenes 6-7 are a drawn cutaway (sky / ocean / seabed): falling spacecraft, Mir 2001, ISS ~2030 (ghost).
- Timing: `words.py` (faster-whisper medium) -> `words_<lang>.json`; `beats.py` -> `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` -> `out/nemo_<lang>.mp4` (with music only).
- Facts: NOAA (≈2688 km, spacecraft cemetery), NASA (ISS deorbit ~2030), Britannica (Mir, 23.03.2001). Corner logo 122 px.
