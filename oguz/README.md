# oguz — «Огузы: от Сырдарьи до Анатолии» (KZ + RU)
Map-history reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield).
Voices: ElevenLabs eleven_v4, one take each — KZ Ерсұлтан, RU Egor energetic (`vo_kk.mp3`, `vo_ru.mp3`).

- Engine: 2D canvas over NASA Blue Marble (from `caspian/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Data: `prep_tex.py` + `grade.py` -> `tex/` (world, eur, syr); `prep_shapes.py` -> `shapes.json` (Natural Earth 10m + hand-drawn Zhetysu, Oghuz state, Seljuk route).
- Timing: `words.py` (faster-whisper) -> `words_<lang>.json`; `beats.py` -> `beats.json`, `caps_<lang>.json`, `vo_<lang>_p.wav` (3 s quiz pause inserted).
- Build: `./build.sh ru|kk` (sfx + music + mix + record + mux) -> `out/oguz_<lang>.mp4`; `./rerec.sh` re-records the picture only.
- Photo: `photos/zhankent.jpg` — Zhankent-1.jpg, Yakov Fedorov, CC BY-SA 4.0, Wikimedia Commons (credit shown on screen).
- Corner logo 122 px high (bigger since 18.11.2026, anti-theft).
