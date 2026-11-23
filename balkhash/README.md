# balkhash — «Балқаш: бір көл, екі су» / «Балхаш: одно озеро, две воды» (KZ + RU)
Batch 10, script 3. JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield), one real photo overlay.
Voice: Arunur's own ElevenLabs voice «Arnur» (eleven_v4, one take per language): `vo_ru.mp3`, `vo_kk.mp3`.

- Engine: 2D canvas over NASA Blue Marble (from `aral/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Textures: `prep_tex.py` (tile C1) + `grade.py` -> `tex/bal.jpg` (240 px/deg); `prep_s2.py` -> `tex/strait.jpg`
  (Copernicus Sentinel-2 L2A mosaic of the Uzynaral strait / Saryesik peninsula, 74.95–76.05E, 45.95–47.3N, 900 px/deg), feathered in the page.
- Shapes: `prep_shapes.py` (Natural Earth 10m): lake split at 75.52E into west/east, Ile (+Künes) from the Eastern Tian Shan, KAZ incl. Baikonur, CHN,
  border lines, Aral 1960/today inset. Karatal, Lepsy, Ayagoz are schematic (traced from the texture).
- Voice timing: `words.py` (faster-whisper medium) -> `words_<lang>.json`; `prep_vo.py` trims the leading silence and stretches the quiz pause to 3 s
  -> `vo_<lang>_x.wav`, `words_<lang>_x.json`; `beats.py` (word indices) -> `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` -> `out/balkhash_<lang>.mp4` (with music). Corner logo 122 px, CTA = link in the profile header.
- Photo: `photos/shore.jpg` = Commons «Lake Balkhash 1588.jpg» (public domain, athineos), 960 px thumb.
- Facts (script sources): География-21, Kazhydromet: Ile ≈ 80 % of inflow, Uzynaral strait ≈ 3–4 km, length 600+ km; mean depth ≈ 6 m.
