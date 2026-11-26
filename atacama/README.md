# atacama — «Он төрт жыл жаңбырсыз» / «14 лет без дождя» (KZ + RU)
Geography batch of 26.11.2026, script 5. Arica: 173 months without rain (1903–1918); the Atacama and its three causes (cold Peru current,
Andean rain shadow, subtropical high), Mars-like soil (NASA rover tests), size ≈ Pavlodar oblast, the flowering desert, ENT question on cold currents.
GEO-KARTA script, code only (no Higgsfield). JAS EDUCATION brand, dark satellite globe, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `tyn/` (<- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map (`fetch_data.sh` + `prep_map.py`): `tex/main.jpg` South America lon -90..-30, lat -50..10, 60 px/deg; `tex/detail.jpg` Atacama lon -76..-64, lat -28..-16,
  240 px/deg (NASA Blue Marble NG B1+B2, Mapzen Terrarium relief); `dem.bin` Andes heights 8 samples/deg; `tex/world.jpg` from tyn/.
  `shapes.json`: Natural Earth borders, Chile, the Atacama core (hand-drawn strip clipped to land, ≈100 000 km², approximate), Pavlodar oblast.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language). KZ: `SLOT=51.04,51.80 python3 prep_vo.py kk` splices the approved
  «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`. `words.py` -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py`, `mix.py`. Build: `./build.sh kk|ru` -> `atacama_<lang>.mp4`.
- Facts (script sources): Atacama Desert (Wikipedia: ~105 000 km², Humboldt current, rain shadow, NASA tests, desierto florido),
  Arica record 173 months (Guinness), Pavlodar oblast ~125 000 km².
