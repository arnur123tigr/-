# kulja — «Қытай өз жерін 9 миллион рубльге сатып алды» (KZ)
Treaty of St Petersburg 1881: Kulja, 9 million roubles, the Uyghurs and Dungans moving to Zhetysu. GEO-KARTA script, KZ only, ~98 s,
code only (no Higgsfield). JAS EDUCATION brand, dark satellite globe, one continuous camera flight (Google-Earth-like), 1080x1920 30 fps.

- Engine: Three.js satellite globe from `semey/` (<- kaganat/): `scene.html?lang=kk` with deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` from semey/; `tex/detail.jpg` = Ili valley + Zhetysu, lon 74..86, lat 41..47, 240 px/deg
  (`fetch_data.sh` + `prep_map.py`: NASA Blue Marble NG C1, Mapzen Terrarium z9 relief). `shapes.json`: Natural Earth 10m borders, KZ/CN, Alaska, Ili.
  Historical areas (Ili territory, the Livadia part, the west edge kept by Russia, the Uyghur district, Zhetysu) are hand-drawn approximations in scene.html.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take, `vo_kk_take.mp3`). `prep_vo.py` shortens long pauses and splices the approved
  «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`; `words.py` (faster-whisper medium) -> `w_kk.json`; `timing.py` -> `vo_kk.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh` -> `kulja_kk.mp4`.
- Facts (script sources): Jas Edu lesson 37; Treaty of Saint Petersburg (1881), Treaty of Livadia, Ili crisis; Alaska 1867 = $7.2 M ≈ 11 M roubles.
