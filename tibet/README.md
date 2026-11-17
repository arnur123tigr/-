# Почему самолёты не летают над Тибетом (remake, RU + KZ, CTA «GEO»)
Remake of a screen-recorded English IG reel (Tibetan Plateau no-fly zone), JAS EDUCATION satellite-map look, 1080x1920. RU 63 s, KZ 71 s.
Voices (ElevenLabs eleven_v4, one take each): RU Egor energetic, KZ Ерсұлтан (`vo_ru.mp3`, `vo_kk.mp3`).

- Engine: `engine.js` from `britain/` (2D canvas over NASA Blue Marble). `tex/tibet.jpg` = Blue Marble July C1+D1 crop lon 66..108 lat 18..44 at 120 px/deg (`prep_tex.py`, `grade.py`).
- `shapes.json` (`prep_shapes.py`): Natural Earth «Plateau of Tibet» (smoothed), metropolitan France, borders.
- `beats.json` / captions `caps_<lang>.json` from `beats.py` (whisper word times, script text). `scene.html?lang=ru|kk`.
- Scenes: planes avoiding Tibet, ×5 France, flight radar with an empty hole, 3 reasons, altitude section (4 500 / 10 000 / 3 000 m, Everest), weather, airports, CTA «GEO» + JAS end card.
- Build: `./build.sh ru` / `./build.sh kk` -> `out/tibet_<lang>[ _no_music].mp4` (deliverables re-encoded at crf 21).
