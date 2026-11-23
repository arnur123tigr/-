# attila — «Рим далаға салық төледі: Аттила» / «Рим платил дань степнякам: Аттила» (KZ + RU)
Batch 10, script 2. Dark night-satellite map of Eurasia, JAS EDUCATION style, 1080x1920, + 2 Higgsfield film shots (scene 1 Hun rider over a burning Roman camp, scene 5 Attila and the Roman envoys with gold).
Xiongnu → Huns? (hypothesis) → 370 Bosporan kingdom → 375 across the Volga, Ostrogoths → Great Migration → Pannonia, Attila 434, «Scourge of God» →
tribute 700 → 2100 lb of gold → Gaul 451, Catalaunian Fields → Italy, before Rome → 453 death, the empire breaks up → ENT card → CTA "link in profile header".

- Engine: 2D canvas over NASA Blue Marble (`engine.js`, `helpers.js`, `scene.html?lang=ru|kk`, deterministic async `render(t)`), copied from `beibars/`.
- Film shots: `hf/s1.jpg`, `hf/s5.jpg` (stills); `prep_clips.sh` extracts the Kling clips to `clips/s<k>/NNNN.jpg` + `clips/clips.json`; without them the stills get a slow push-in.
- Shapes: `prep_shapes.py` (Natural Earth geojson) -> `shapes.json`: Roman Empire c.450 (schematic), Mongolia, rivers. Hun lands, Pannonia and arrows are schematic, in scene.html.
- Textures: `prep_tex.py tex reg -12 78 28 62 40` + `grade.py` (Blue Marble tiles B1, C1); `tex/world.jpg` from teniz/.
- Voices: ElevenLabs eleven_v4, one take each, Arunur's own voice «Arnur»; earlier Egor/Ерсұлтан takes kept in takes/.
- Timing: `words.py` (faster-whisper medium) -> `words_<lang>.json`; `beats.py` -> `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` -> `out/attila_<lang>.mp4` (with music).
