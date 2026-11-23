# alma — «Все яблоки мира родом из Алматы» / «Әлемдегі барлық алма Алматыдан шыққан» (KZ + RU)
Batch 10, script 12. JAS EDUCATION satellite-map style, 1080x1920, code + 1 Higgsfield shot.
Voice: Arunur's own cloned ElevenLabs voice «Arnur» (dYmt55JYwdFpUMbmVszd), eleven_v4, one take per language (`vo_<lang>_raw.mp3`).

- Engine: 2D canvas over NASA Blue Marble (from `almaty/` → `teniz/`): `engine.js`, `helpers.js`, `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Textures (`prep_tex.py` + `grade.py`, tile C1): `tex/jet.jpg` (Ile + Jungar Alatau, 160 ppd), `tex/silk.jpg` (Silk Road 0–84E, 40 ppd), plus `alm`, `ca`, `world` from almaty/.
- `prep_shapes.py` → `shapes.json`: NE 10m KZ (with Baikonur), borders, «Alataw Mts.» polygon (Jungar Alatau).
- Higgsfield (Arunur approved, 9.5 credits): Nano Banana Pro still `hf/forest.png` + Kling 3.0 Turbo 5 s `hf/forest.mp4` (716x1284); frames: minterpolate 30 fps + lanczos 1080x1920 → `hf/frames/` (not committed, regenerate with the ffmpeg line in the thread notes).
- Timing: `words.py` (faster-whisper medium) → `words_<lang>_raw.json`; `prep_vo.py <lang>` stretches the quiz pause to 3 s → `vo_<lang>.mp3`, `words_<lang>.json`; `beats.py` → `beats.json`, `caps_<lang>.json`.
- Build: `./build.sh ru|kk` → `out/alma_<lang>.mp4` (with music).
- Facts (script sources): Vavilov in Alma-Ata 1929; Golden Delicious genome 2010 (Velasco et al.) → main ancestor Malus sieversii; aport brought to Verny 1865 from Voronezh (Egor Redko); Malus sieversii in the Red Book of KZ.
