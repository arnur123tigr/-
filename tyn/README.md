# tyn — «Өз жерінде азшылық: Тың игеру» / «Меньшинство на своей земле: целина» (KZ + RU)
Batch 11, script 5. Virgin Lands campaign 1954–1960: the decision in Moscow, Shayakhmetov removed, 25.5 M ha ploughed (vs Great Britain),
trains and 600+ state farms, the Virgin Lands Krai 1960, Akmola → Tselinograd, dust storms, census 1959 (30 %) → 2021 (70 %), Tselinograd → Astana.
GEO-KARTA script, code only (Arunur chose no Higgsfield: scenes 4 and 9 are map animations). JAS EDUCATION brand, dark satellite globe, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `kulja/` (<- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` from kulja/; `tex/detail.jpg` = northern Kazakhstan lon 58..82, lat 47..56.5, 120 px/deg
  (`fetch_data.sh` + `prep_map.py`: NASA Blue Marble NG C1, Mapzen Terrarium z7 relief). `shapes.json`: Natural Earth 10m borders, Kazakhstan,
  United Kingdom, the five oblasts of 1960 (modern provinces; Kokchetav oblast hand-drawn and cut out of North Kazakhstan and Akmola, approximate).
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language). `prep_vo.py` shortens long pauses; KZ: `SLOT=70.73,71.49 python3 prep_vo.py kk`
  splices the approved «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`. `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `tyn_<lang>.mp4`.
- Facts (script sources): Virgin Lands campaign (Wikipedia), Shayakhmetov removed Feb 1954, Virgin Lands Krai 1960–1965, Akmolinsk renamed 1961,
  census 1959 (Kazakhs 30.0 %, Russians 42.7 %), census 2021 (Kazakhs 70.4 %, Russians 15.5 %), Great Britain/UK ≈ 24.4 M ha.
