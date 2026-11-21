# beibars — «Мысыр сұлтаны Дешті Қыпшақтан» / «Султан Египта из Дешт-и-Кыпчака» (KZ + RU)
Batch 9, script 5. Dark satellite map, JAS EDUCATION style, 1080x1920, code only (no Higgsfield). Route of Baibars:
Cairo (hook, crown) → Desht-i-Kipchak ~1223 → Mongol invasion, captivity, chain to the Crimean slave market → by sea to Egypt →
mamluk, army, commander → Mongols via Baghdad / Aleppo / Damascus, Ain Jalut 1260 → sultan 1260–1277, line back to the steppe →
ENT quiz with a 3 s countdown → loop to the opening → CTA "link in profile header".

- Engine: 2D canvas over NASA Blue Marble (`engine.js`, `helpers.js`, `scene.html?lang=ru|kk`, deterministic `render(t)`), copied from `hormuz/`.
  Turquoise rivers + borders from Natural Earth (`prep_shapes.py` -> `shapes.json`). Desht-i-Kipchak polygon and routes are schematic.
- Textures: `prep_tex.py tex reg 14 84 16 60 40 lev 28 40 26 37 120` + `grade.py` (Blue Marble tile C1); `tex/world.jpg` from teniz/.
- Photos (optional): `photos/ph1.jpg` (Baibars mosque, Cairo), `photos/ph2.jpg`; the scene skips a missing one.
- Voices: ElevenLabs eleven_v4, one take each — RU Egor (BXpVl3OTz6ZGDqlYtXXB), KZ Ерсұлтан; `pause.py` inserts the quiz pause (takes/ keeps the raw takes).
- Timing: `words.py` (faster-whisper medium) -> `words_<lang>.json`; `beats.py` -> `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` -> `out/beibars_<lang>.mp4` (with music). `record.js out fps from to` records a part only.
