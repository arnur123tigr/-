# gulag — «Қазақ даласы — КСРО-ның түрмесі» / «Казахская степь — тюрьма СССР» (KZ + RU)
GULAG in Kazakhstan: Karlag (Dolinka, ~300 km), the deportations (Koreans 1937, Germans 1941, Chechens 1944), Steplag and the Kengir rising (1954, 40 days, tanks),
ALZhIR 35 km from Astana, Gulbahram Seifullina, the kurt thrown over the fence. GEO-KARTA batch 11 script №6, ~94 s, JAS EDUCATION brand, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `kulja/` (<- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` as in kulja/; `tex/detail.jpg` = central Kazakhstan lon 66..76, lat 46..53, 240 px/deg (`fetch_data.sh` + `prep_map.py`).
  Camp zones (Karlag, Steplag) and the aul are approximate.
- Film shots (frames 8 and 10): Higgsfield, Nano Banana Pro stills `hf/s8.png`, `hf/s10.png` (s10 made with s8 as reference), animated with Kling 3.0 Pro 5 s;
  `prep_clips.sh` turns `hf/video/s<n>.mp4` into 60 fps frames in `clips/` (not committed; Kling clips are Higgsfield jobs 6864248d…, 84801421…).
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language, `vo_<lang>_take.mp3`). `prep_vo.py` shortens long pauses; KZ: the approved
  «ҰБТ-да» clip from `animation/common/ubt_kk_parts/` replaces 72.27–72.82 s. RU says «Е Эн Тэ». `words.py` -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py`. Build: `./build.sh kk|ru` -> `gulag_<lang>.mp4`.
- Facts (script sources): Karlag 1931–1959, ~300 km N–S; Kengir uprising 16 May – 26 June 1954; ALZhIR 1938–1953, ~18 000 women, ~35 km from Astana; 31 May.
  Moscow–Karaganda distance on screen is the computed great-circle distance (~2 450 km).
