# aktaban — «Ақтабан: табаны ағарғанша қашқан халық» / «Актабан: народ, бежавший до белых пяток» (KZ + RU)
1723, «Ақтабан шұбырынды, Алқакөл сұлама»: the Dzungar invasion, the three routes of the zhuzes (Khojent, Samarkand, Khiva/Bukhara, the Yaik),
the battles of 1726-1730 and the end of the Dzungar Khanate (1755-1758). GEO-KARTA script (batch 11 №3), ~80 s, 1080x1920 30 fps, JAS EDUCATION brand.

- Engine: Three.js satellite globe from `kulja/` (<- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` from kulja/; `tex/detail.jpg` = Kazakhstan + Central Asia, lon 50..90, lat 35..52, 100 px/deg, with the Aral
  filled back to its historic shore (Natural Earth lakes_historic). `fetch_data.sh` + `prep_map.py`. Dzungar Khanate, routes, battle places: hand-drawn approximations.
- Film shots (Higgsfield): frame 1 (bare feet on a salt flat) and frame 9 (the boy at the night fire): Nano Banana Pro stills + Kling 3.0 5 s, `clips/s1.mp4`, `clips/s9.mp4`
  (frames are extracted to clips/s1/, clips/s9/, see build.sh).
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language, `vo_<lang>_take.mp3`). `prep_vo.py` splices the approved «ҰБТ-да» clip
  (animation/common/ubt_kk_parts/) and shortens long pauses; `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed with a sybyzgy-like flute), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru`.
- Facts (script sources): Wikipedia «Годы великого бедствия» / «Ақтабан шұбырынды»; Ordabasy 1726, Bulanty 1728, Anyrakai 1729/1730; Dzungar Khanate destroyed by Qing 1755-1758.
