# astana — «Почему в Астане так холодно» (KZ + RU)
GEO-KARTA reel, JAS EDUCATION satellite-map style, 1080x1920, code only (no Higgsfield). Engine copied from `teniz/`.
Voices: ElevenLabs eleven_v4, one take each — RU Egor energetic (`vo_ru.mp3`), KZ Ерсұлтан (`vo_kk.mp3`).

- Scenes: hook (Astana ring + snow), coldest capitals (Ulaanbaatar −21, Astana −14, Ottawa −10, Moscow −6, January means), −14 °C,
  1/3 far from the ocean (lines to Atlantic/Pacific, warm air dies out), 2/3 no mountains in the north (Arctic air arrows),
  3/3 Siberian High (rotating isobars), ENT stamp, records +41,6 (1936) / −51,6 (1893) thermometer, 93 °C ≈ boiling water vs ice, CTA link.
- Timing: RU words from faster-whisper medium (`words.py`), KZ words from ElevenLabs Scribe; `beats.py` -> `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` -> `out/astana_<lang>.mp4` (with music only).
- Facts (pogodaiklimat.ru 35188, Environment Canada): Astana January ≈ −14 °C, record −51,6 °C / +41,6 °C; Moscow ≈ −6, Ottawa ≈ −10, Ulaanbaatar ≈ −21.
