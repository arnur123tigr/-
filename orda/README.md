# orda — «Қазақтың тұңғыш астанасы бүгін Ресейде» / «Первая столица казахов сегодня в России» (KZ + RU)
Batch 11 GEO-KARTA script 1: the lands that left Kazakhstan in 1920–1936 (Orenburg, Omsk, the Bukey Horde part at Astrakhan, Karakalpakstan).
JAS EDUCATION brand, dark satellite globe, one continuous camera flight, frame 4 = one Higgsfield film shot. 1080x1920 30 fps, ~90 s.

- Engine: Three.js satellite globe from `kulja/` (<- semey/ <- kaganat/): `scene.html?lang=kk|ru` with deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` from kulja/; `tex/detail.jpg` = Orenburg, lon 53..57.5, lat 50.5..53, 240 px/deg
  (`fetch_data.sh` + `prep_map.py`: NASA Blue Marble NG C1, Mapzen Terrarium z9 relief). `shapes.json`: Natural Earth 10m borders and admin-1
  (Orenburg, Omsk, Astrakhan, Karakalpakstan, Zhambyl). The Bukey Horde, the old Akmola oblast and the 1920s Kazakh ASSR are approximations (prep_map.py).
- Film shot: `hf/s4.jpg` (Higgsfield Nano Banana Pro) animated with Kling 3.0 (5 s) -> `hf/video/s4.mp4` -> `prep_clips.sh` -> `clips/s4/` (not committed).
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take each, `vo_<lang>_take.mp3`). `prep_vo.py` shortens long pauses; KZ: splices the approved
  «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`. `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `orda_<lang>.mp4`.
- Facts (script sources): Jas Edu lessons 47–48; Kirghiz (Kazakh) ASSR, capital Orenburg 1920–1925; Akmola oblast (centre Omsk, 1868–1917); Bukey Horde;
  Karakalpak ASSR (1925 KASSR, 1930 RSFSR, 1936 UzSSR), ~166 600 km² vs Zhambyl ~144 000 km²; census 2021 (~590 000 Kazakhs in Russia), 2010 (Astrakhan 14.7 %).
