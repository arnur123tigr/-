# aral — «Куда исчезло Аральское море» / «Арал теңізі қайда жоғалды?» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield).
Voices: ElevenLabs eleven_v4, one take each — RU Egor energetic, KZ Ерсұлтан (`vo_ru.mp3`, `vo_kk.mp3`).

- Engine: 2D canvas over NASA Blue Marble (from `nemo/` / `oguz/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Data: `prep_tex.py` (tile C1 from assets.science.nasa.gov into /home/user/data) + `grade.py` -> `tex/cas.jpg`, `tex/aral.jpg`; `prep_aral.py`
  erases the 2004 water inside the 1960 shoreline (inpaint -> dry seabed) and writes `shapes.json`: Natural Earth 10m (lakes_historic Aral 1960 ≈ 67 600 km²,
  North/South Aral today, Syr/Amu Darya, KAZ incl. Baikonur, Lithuania) + 61 drying contour levels (field d_shore/(d_shore+d_remnant)).
- Canals are schematic (Karakum canal, Khorezm, Bukhara, Hungry steppe, Kyzylorda, Fergana). Kok-Aral dam line is approximate.
- Timing: `words.py` (faster-whisper) -> `words_<lang>.json`; `raw_beats.json` + `beats.py` -> `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` -> `out/aral_<lang>.mp4` (with music only). Corner logo 122 px.
- Facts: Britannica (≈68 000 km² in 1960, 4th largest lake), NASA Earth Observatory (shrinking, east basin dry by 2014), World Bank (Kok-Aral dam 2005, North Aral fish back).
