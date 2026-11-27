# syrym — «Патшамен де, өз ханымен де» / «И с царём, и со своим ханом» (KZ + RU)
Batch 27.11 history script 2: Syrym Datuly's uprising in the Junior Zhuz, 1783–1797 (decree of 1782, Nuraly khan exiled to Ufa 1786,
Igelstrom's reform, Ilek 1792, Esim khan killed 1797, Khiva, the Bukey Horde 1801). JAS EDUCATION brand, dark satellite globe,
one continuous camera flight, every frame in code (no Higgsfield). 1080x1920 30 fps, ~94 s.

- Engine: Three.js satellite globe from `orda/` (<- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru` with deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/*`, `dem.bin` from orda/ (NASA Blue Marble NG, Mapzen Terrarium). `shapes.json` = orda's Natural Earth shapes + `add_shapes.py`
  (hand-drawn approximations: the Junior Zhuz, the Baibakty pastures between the Zhaiyk and the Oiyl; the Ural line; the Bukey Horde from orda).
  The khans' camps are approximate points. Portraits (Syrym, Nuraly, Esim) are drawn in code (Kazakh börik / khan's hat with owl feathers).
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take each, `vo_<lang>_take.mp3`). `prep_vo.py` shortens long pauses; KZ: `SLOT=78.84,79.47`
  splices the approved «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`. `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `syrym_<lang>.mp4`.
- Facts (script sources): Jas Edu lesson 30–31 «С. Датұлы»; ru.wikipedia «Восстание Срыма Датова». Syrym died in Khiva (1802, not shown).
