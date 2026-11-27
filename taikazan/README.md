# taikazan — «Тайқазан 54 жыл Ленинградта тұрды» / «Тайказан 54 года простоял в Ленинграде» (KZ + RU)
Batch 27.11 «карта-история» script 4: the Taikazan of the Khoja Ahmed Yasawi mausoleum (cast 1399 by order of Amir Timur, master Abd al-Aziz Tabrizi),
taken to the Hermitage in Leningrad in 1935 "for one exhibition" of Iranian art, returned to Turkestan in 1989.
JAS EDUCATION brand, dark satellite globe, one continuous camera flight, code only (no AI images). 1080x1920 30 fps, ~80 s.

- Engine: Three.js satellite globe from `orda/` (<- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru` with deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin`, `shapes.json` from orda/; `tex/detail.jpg` = Turkestan and the Syr Darya, lon 67..69.5, lat 42.6..44,
  240 px/deg (`fetch_data.sh` + `prep_map.py tex`: NASA Blue Marble NG C1, Mapzen Terrarium z9 relief).
- Drawn in code: the mausoleum plan (simplified, the Kazandyk hall in the middle), the cauldron with a 1.8 m man at true scale (Ø 2.45 m),
  Timur's portrait, the Hermitage front, baths, meat / water icons. The 1935 road follows the railway (Kyzylorda, Aral, Aktobe, Orenburg, Samara, Moscow), 3 237 km.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take each, `vo_<lang>_take.mp3`). `prep_vo.py` shortens long pauses, KZ splices the approved
  «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`, then both languages 5 % faster. `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `taikazan_<lang>.mp4`.
- Facts (script sources): en.wikipedia Mausoleum of Khoja Ahmed Yasawi; ru.wikipedia Тайказан (≈2 t, Ø 2.45 m, ≈3 000 l; Hermitage 1935 for the
  III International Congress on Iranian Art; returned 1989; made for water).
