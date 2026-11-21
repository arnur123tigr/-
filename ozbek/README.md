# ozbek — «Бабаларымыз «өзбек» аталған» / «Наших предков звали узбеками» (KZ + RU)
Map-history reel (batch 9, script 4), JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield).
Voices: ElevenLabs eleven_v4, one take each — KZ Aruzhan, RU Alina (`vo_kk.mp3`, `vo_ru.mp3`).

- Engine: 2D canvas over NASA Blue Marble (from `oguz/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Data: `prep_tex.py tex reg 44 90 34 58 60 mav 58 82 36 47 120` + `grade.py` -> `tex/`; `prep_shapes.py` -> `shapes.json`
  (Natural Earth 10m + hand-drawn approximate Uzbek ulus, Moghulistan, Maverannahr, Chu river).
- Timing: `words.py` (faster-whisper) -> `words_<lang>.json`; `beats.py` -> `beats.json`, `caps_<lang>.json`, `vo_<lang>_p.wav` (3 s quiz pause).
- Build: `./build.sh ru|kk` -> `out/ozbek_<lang>.mp4`.
- Manuscript overlay: drawn by code unless `photos/photo.json` + an image are provided (`{"file": ..., "focus": [x,y], "zoom": 1, "credit": ...}`).
- Drawn Turkic khans (`khanDisc`): borik with fur brim and gold finial, moustache, chapan. Corner logo 122 px.
