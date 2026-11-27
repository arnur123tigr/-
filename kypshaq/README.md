# kypshaq — «Венгриядағы қыпшақтар» / «Кипчаки в Венгрии» (KZ + RU)
Batch of 27.11.2026, script 3. Kunság in Hungary («land of the Cumans»), Desht-i-Kipchak from the Irtysh to the Danube, three names of one people,
Batu 1237, Khan Köten leads his people west (40 000 families, Rogerius), Béla IV accepts them in 1239, Köten killed in Pest 1241, the return and Kunság,
the Codex Cumanicus (Venice, 1303), King László IV «the Cuman», ENT question (Nasir Khusraw). GEO-KARTA script, code only (no Higgsfield).
JAS EDUCATION brand (bigger corner logo), dark satellite globe, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `atacama/` (<- tyn/ <- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map (`fetch_data.sh` + `prep_map.py`): `tex/main.jpg` lon 4..90, lat 32..62, 60 px/deg; `tex/detail.jpg` Hungary lon 14..24, lat 44..50, 240 px/deg
  (NASA Blue Marble NG C1, Mapzen Terrarium relief); `dem.bin` 8 samples/deg; `tex/world.jpg` from atacama/.
  `shapes.json`: Natural Earth borders, Kazakhstan, Hungary, rivers; Desht-i-Kipchak (hand-drawn steppe belt, clipped to land, approximate);
  Kiskunság and Nagykunság (hand-drawn, approximate). Portraits (Köten, Béla IV, László IV, Nasir Khusraw) are drawn in code, symbolic.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language). KZ: `SLOT=76.80,77.65 python3 prep_vo.py kk` splices the approved
  «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`; RU: `python3 prep_vo.py ru` (pauses only). `words.py` -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py`. Build: `./build.sh kk|ru` -> `kypshaq_<lang>.mp4`.
- Facts (script sources): Wikipedia Köten, Cumania, Kunság, Codex Cumanicus, Ladislaus IV of Hungary. Elizabeth the Cuman as Köten's daughter is the majority view, not certain.
