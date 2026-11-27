# qamal — «Бізге қарсы салынған қалалар» / «Города, построенные против нас» (KZ + RU)
Batch of 27.11.2026, script 1. Қасірет белдеуі: the Russian fortress lines round the Kazakh steppe — Omsk 1716, Semey 1718, Öskemen and the Koryakov post (Pavlodar) 1720,
Orenburg 1735, the ban on the right bank of the Ural, the Uy line (770 km), Petropavl 1752, and the last one, Verny 1854 = today's Almaty. ҰБТ/ЕНТ question, CTA = link in the profile header.
Map story, code only (no Higgsfield). JAS EDUCATION brand, dark satellite globe, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `karagie/` (<- tyn/ <- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` from karagie/; `tex/detail.jpg` = Almaty and the Alatau (240 px/deg), `tex/peak.jpg` = north-east Kazakhstan (120 px/deg)
  (`fetch_data.sh` + `prep_map.py`: NASA Blue Marble NG C1, Mapzen Terrarium relief). `shapes.json`: Natural Earth borders, Kazakhstan, rivers (Irtysh, Ishim, Ural, Tobol, Or, Ilek;
  the Uy and the Malaya Almatinka drawn by hand, approximate), the right bank of the Ural (a band on the right of the flow, Orsk -> the sea).
  The fortress lines are schematic: Orenburg line along the Ural, Orsk -> Verkhneuralsk, Uy line, New Ishim line (Zverinogolovskaya -> Petropavl -> Omsk), Irtysh line.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language, `vo_*_take.mp3`). `prep_vo.py` speeds the take up 6 % and shortens long pauses;
  KZ: `SLOT=73.40,74.10 python3 prep_vo.py kk` splices the approved «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`. `words.py` -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `qamal_<lang>.mp4`.
- Notes: «7» is the reel's own counter (Omsk, Semey, Öskemen, Koryakov, Orenburg, Petropavl, Verny), there were many more forts. Verny is drawn as a pentagon (the 1854 fortification was five-sided).
  Peter I is shown as a crown medallion (no portrait: Wikimedia blocks the cloud). The Younger Zhuz outline is schematic.
