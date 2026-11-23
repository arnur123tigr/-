# stoletka — «Жүз жылдық соғыс 100 жыл емес» / «Столетняя война длилась не 100 лет» (KZ + RU)
Batch 10, script 7. Dark satellite map of Western Europe (the script asked for parchment: replaced by the satellite rule), JAS EDUCATION style, 1080x1920.
Hook 100 → 116 · ENT trap 1337–1453 · England red / France blue, the four lands (Normandy, Anjou, Aquitaine, Flanders) · two crowns, one throne ·
war/truce timeline · Black Death · Jacquerie 1358, Wat Tyler 1381 · 1428 occupation, Orléans besieged, Joan's road Domrémy → Chinon → Orléans ·
2 Higgsfield film shots (Orléans 1429, Rouen 1431) · reconquest to 1453, Calais · Wars of the Roses · ENT quiz with a 3 s countdown · loop to 116 + CTA.

- Engine: 2D canvas over NASA Blue Marble (`engine.js`, `helpers.js`, `scene.html?lang=ru|kk`, async deterministic `render(t)`), from `beibars/`.
- Shapes: `prep_shapes.py` (Natural Earth 10m geojson: French departments / Belgian provinces approximate the medieval lands).
- Textures: `prep_tex.py tex reg -14 18 38 62 60 det -6 9 42 52.5 200` + `grade.py` (Blue Marble tiles B1, C1).
- Film shots: `hf/s6.jpg`, `hf/s7.jpg` (Nano Banana Pro). If `clips/clips.json` exists ({"s6": frames, "s7": frames}), frames `clips/s6/0001.jpg…` (30 fps) replace the stills.
- Voice: Arunur's own ElevenLabs voice «Arnur», eleven_v4, one take each; `pause.py` adds the 3 s quiz pause (raw takes in takes/).
- Timing: `words.py` (faster-whisper medium) → `words_<lang>.json`; `beats.py` → `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` → `out/stoletka_<lang>.mp4` (synth music + SFX from `sfx.py`, mix from `mix.py`).
