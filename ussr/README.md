# ussr — «КСРО-дан ең соңғы болып шықтық» / «Мы вышли из СССР последними» (KZ + RU)
Batch of 27.11.2026, script 5. The USSR falls apart on the map: Lithuania 11.03.1990, the August 1991 coup in Moscow, the chain of declarations
(dates of the republics' independence declarations), the 1991 referendum (Kazakh SSR ≈94 % «for»), Belovezh 8.12, Kazakhstan 16.12.1991 (last; counter stops
at 14/15 because Russia made no separate declaration), Almaty 21.12 (CIS, 11 flags), Gorbachev resigns 25.12, ҰБТ/ЕНТ question.
GEO-KARTA script, code only (no Higgsfield). JAS EDUCATION brand, dark satellite globe, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `karagie/` (<- tyn/ <- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` unchanged (NASA Blue Marble NG, Mapzen Terrarium relief). `prep_map.py` writes `shapes.json`:
  the 15 republics from Natural Earth 10m countries (today's borders = the SSR borders), their union, land borders.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language). `prep_vo.py` shortens long pauses; KZ:
  `UBTCLIP=.../ubt_kk_parts/ubt_bul.mp3 SLOT=73.76,74.83 python3 prep_vo.py kk` splices the approved «Бұл ҰБТ» clip (the clone said «өбете»).
  `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `ussr_<lang>.mp4`.
- Flags in the Belovezh and Almaty scenes are today's flags, drawn simplified in code.
