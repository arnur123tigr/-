# karagie — «Қазақстан теңізден төмен» / «Казахстан ниже уровня моря» (KZ + RU)
Geography batch of 26.11.2026, script 2. Karagiye Depression (−132 m, 5th deepest land depression), the Bayterek (97 m) fits inside,
Khan Tengri (7 010 m) and the 7 142 m difference (≈ 70 Bayterek towers), the Caspian lowland below sea level, Atyrau ≈ −20 m, ҰБТ/ЕНТ question.
GEO-KARTA script, code only (no Higgsfield). JAS EDUCATION brand, dark satellite globe, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `tyn/` (<- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` from tyn/; `tex/detail.jpg` = Mangystau + Atyrau (lon 48..56, lat 41..48.5, 200 px/deg),
  `tex/peak.jpg` = Khan Tengri (lon 78.5..81.5, lat 41.5..43.3, 240 px/deg) (`fetch_data.sh` + `prep_map.py`: NASA Blue Marble NG C1, Mapzen Terrarium z9 relief).
  `shapes.json`: Natural Earth borders and Kazakhstan; land below 0 m round the Caspian (Terrarium z7, land only); the Karagiye bowl (z9, below −40 m);
  the west-east height profile Karagiye -> Khan Tengri (z7, approximate, ends pinned to −132 and 7 010 m).
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language). `prep_vo.py` shortens long pauses; KZ: `SLOT=48.07,48.68 python3 prep_vo.py kk`
  splices the approved «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`. `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `karagie_<lang>.mp4`.
- Facts (script sources): Karagiye −132 m (Wikipedia; 5th by depth per the textbook «13. Қазақстанның жер бедері»), Dead Sea −430, Lake Assal −155, Turpan −154,
  Qattara −133, Khan Tengri 7 010 m, Atyrau ≈ −20 m, Bayterek 97 m.
