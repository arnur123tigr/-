# teniz — «Самая большая страна без выхода к морю» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield).
Voices: ElevenLabs eleven_v4, one take each — RU Egor energetic (`vo_ru.mp3`), KZ Ерсұлтан (`vo_kk.mp3`).

- Engine: 2D canvas over NASA Blue Marble (from `nemo/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Data: `prep_tex.py` (tile C1 from assets.science.nasa.gov into /home/user/data) + `grade.py` -> `tex/ca.jpg` (Central Asia), `tex/eu.jpg` (Alps); `tex/world.jpg` from oguz/.
  `prep_shapes.py` -> `shapes.json` (Natural Earth 10m; Kazakhstan merged with Baikonur; Europe's five as km offsets, moved into KZ at true size, see `EUT`).
- Timing: `words.py` (faster-whisper) -> `words_<lang>.json`; `beats.py` -> `beats.json`, `caps_<lang>.json` (beats found from the first word of each fragment).
- Build: `./build.sh ru|kk` -> `out/teniz_<lang>.mp4` (with music only).
- Facts: area 2 724 900 km² (9th); FRA+DEU+ESP+ITA+GBR ≈ 1.93 mn km²; Eurasian pole of inaccessibility 46°17′N 86°40′E, ≈2 510 km from the sea (Garcia-Castellanos & Lombardo 2007); Almaty–Atyrau ≈ 2 000 km straight; Uzbekistan and Liechtenstein are the only doubly landlocked countries. Corner logo 122 px.
