# saiga — «Сайгак: из Красной книги в почти три миллиона» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield).
Voices: ElevenLabs eleven_v4, one take each — RU Egor energetic (`vo_ru.mp3`, 47 s), KZ Ерсұлтан (`vo_kk.mp3`, 53 s); `[proud]` tag from stage three.

- Engine: 2D canvas over NASA Blue Marble (copied from `teniz/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Data: `tex/ca.jpg` (Central Asia, 80 ppd) and `tex/world.jpg` from teniz; `prep_shapes.py` -> `shapes.json` (Natural Earth 10m, Kazakhstan merged with Baikonur).
  The three populations (Betpak-Dala, Ustyurt, Ural) are approximate hand-drawn ranges (`ZONES` in scene.html); herds are clustered dots inside them.
- Drawn assets: saiga silhouette, nose close-up (cold air warmed, dust stopped), Red Book.
- Timing: `words.py` (faster-whisper medium) -> `words_<lang>.json`; `beats.py` (token patterns per sentence) -> `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` -> `out/saiga_<lang>.mp4` (with music only).
- Facts: ~1 mn saigas around 1990, ~21 000 in 2003; 2015 die-off >200 000 in a few weeks (Kock et al., Science Advances 2018);
  2024 aerial count ~2.86 mn (ACBK); Almaty ~2.3 mn people; IUCN Dec 2023 CR -> NT (shown as «Вне угрозы» with the exact status in small print).
