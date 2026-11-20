# almaty — «Почему трясёт Алматы» / «Неге Алматы сілкінеді» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield).
Voices: ElevenLabs eleven_v4, one take each — RU Egor energetic (`vo_ru.mp3`, 44 s), KZ Ерсұлтан (`vo_kk.mp3`, 48 s).

- Engine: 2D canvas over NASA Blue Marble (from `teniz/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Textures: `prep_tex.py` + `grade.py` (Blue Marble tiles C1, D1 in /home/user/data): `tex/ind.jpg` (India–Tibet, 60 ppd), `tex/alm.jpg` (Almaty, 240 ppd), `tex/ca.jpg`, `tex/world.jpg` from teniz/.
- `prep_shapes.py` -> `shapes.json`: Natural Earth 10m countries (KZ + Baikonur), mountain ranges (Tian Shan, Himalayas, Tibet, Pamirs), KZ seismic split
  (red = East KZ, Almaty, Almaty city, Zhambyl, Turkestan oblasts; green = rest, simplified for the ENT map), India–Eurasia boundary from PB2002 (Bird 2003).
- Timing: `words.py` (faster-whisper medium) -> `words_<lang>.json`; `beats.py` -> `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` -> `out/almaty_<lang>.mp4` (with music).
- Facts: India moves north ~4–5 cm/yr (USGS); Nepal Himalayan front (27.2N 85.3E) -> Almaty ≈ 1 950 km; Verny 1887 M≈7.3, Kemin 1911 M≈8 (USGS); peak Talgar 4979 m.
