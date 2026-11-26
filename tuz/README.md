# tuz — «Ең тұзды теңіз — Өлі теңіз емес» / «Самое солёное море — не Мёртвое» (KZ + RU)
Geo batch 26.11.2026, script 4. Salinity in per mille: the Dead Sea is a lake, the ocean 35 ‰, the Baltic ~7 ‰, the Red Sea up to 41 ‰ (no rivers, evaporation),
the Caspian ~13 ‰, the south Aral 100+ ‰, the north Aral freshening behind the Kokaral dam; ENT question at the end, CTA = link in the profile header.
GEO-KARTA script, code only (no Higgsfield). JAS EDUCATION brand, dark satellite globe, 1080x1920 30 fps.

- Engine: Three.js satellite globe from `tyn/` (<- kulja/ <- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` from tyn/; detail textures `tex/dead.jpg`, `tex/aral.jpg`, `tex/baltic.jpg` (`fetch_data.sh` + `prep_map.py`:
  NASA Blue Marble NG C1, Mapzen Terrarium z7 relief). `shapes.json`: Natural Earth 10m borders, Kazakhstan, lakes (Dead Sea, North/South Aral, Aral 1960),
  marine areas (Red Sea + gulfs, Baltic + gulfs, Caspian), desert shores of the Red Sea, rivers into the Baltic.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language). `prep_vo.py` shortens long pauses; KZ: `SLOT=65.09,65.91 python3 prep_vo.py kk`
  splices the approved «ҰБТ-да» clip from `animation/common/ubt_kk_parts/`. `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `tuz_<lang>.mp4`.
- Facts (script sources): Red Sea 36–41 ‰, no permanent rivers; Baltic ~7 ‰; Dead Sea is a lake (~340 ‰); Caspian ~1/3 of ocean salinity; south Aral > 100 ‰, Kokaral dam 2005.
