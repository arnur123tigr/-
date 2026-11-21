# baikonur — «Байқоңыр Байқоңырда емес» / «Космодром Байконур не в Байконуре» (KZ + RU)
Batch 9, script 2. Flat Vector (script palette on JAS colours) + one satellite map scene (MAPS RULE), 1080x1920, code only.
Scenes: rocket + «БАЙҚОҢЫР ≠ БАЙҚОҢЫР» → satellite map Tyuratam vs Baikonyr village (≈320 km) → 1955 test site → 1961 Gagarin, newspaper names the far village →
Leninsk → Baikonur (1995), lease to 2050 → ENT card (1955 / 1961 / 1991, Aubakirov) → quiz with 3-2-1 → CTA "link in profile header" → JAS end card.

- Engine: `engine.js`, `helpers.js` (from hormuz/), `scene.html?lang=ru|kk` (deterministic `render(t)`), `record.js`.
- Map: `tex/world.jpg`, `tex/ca.jpg`, `shapes.json` from teniz/ (NASA Blue Marble, Natural Earth; Kazakhstan merged with Baikonur).
  Village Baikonur (Ulytau) 47.823 N 66.047 E (en.wikipedia), Tyuratam station 45.63 N 63.32 E.
- Voices: ElevenLabs eleven_v4, one take each: RU Egor energetic, KZ Ерсұлтан (`vo_<lang>_raw.mp3`).
  `stretch.py` lengthens the quiz pause to 3.3 s -> `vo_<lang>.mp3`, `words_<lang>.json`.
- Timing: `words.py` (faster-whisper medium) -> `words_<lang>_raw.json`; `beats.py` -> `beats.json`, `caps_<lang>.json`.
- Sound: `sfx.py` (synth SFX + 112 bpm bed), `mix.py` (voice-first). `./build.sh ru|kk` -> `out/baikonur_<lang>.mp4`. Corner logo 122 px.
- Photos (`fetch_photos.sh`; Commons needs a UA with a reuse link): Gagarin 12.04.1961 (TASS / mos.ru, CC BY 4.0, 960 px thumb),
  Aubakirov from the 1996 Kazpost stamp (Commons «ToktarAwbakirov 140x190.jpg», PD-KZ-exempt). No free real photo of him in a spacesuit exists.
