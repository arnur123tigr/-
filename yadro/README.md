# Жердің ортасына дейін қанша қазу керек? / Сколько копать до центра Земли? (3D cutaway)

Vertical reel 1080x1920, 30 fps, RU ~101.8 s, KZ ~103.7 s. Code only (no AI images). JAS EDUCATION brand layer (bigger corner logo, end card, CTA = link in the profile header).
Voice: Arunur's own cloned ElevenLabs voice «Arnur» (eleven_v4, one take per language).

| File | What |
|---|---|
| scene.html | Three.js: Earth (NASA Blue Marble) with a quarter cut out by clipping planes, two cut faces painted with the layers (crust drawn thicker), elevator cabin down the corner edge, little digger; crust "cake" block (ocean / plain / mountains, sedimentary-granite-basalt) with the Kola rig, 12 262 m borehole and an upside-down Everest; 2D overlay: depth gauge, thermometer, Kola satellite inset, quiz with a 3 s timer, captions |
| timing.py | caption script aligned to whisper words; `@wait` inserts the 3 s quiz pause |
| sfx.py / mix.py / build.sh | synthesised effects + music bed, voice-first mix (-14 LUFS), BT.709 encode |
| splice_ubt.py | swaps each spoken «ҰБТ» in the KZ take for one correct clip, keeping the length |
| tex/ | earth.jpg (Blue Marble 4096x2048), kola.jpg (Blue Marble tile C1 crop) |

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small; python3 words.py vo_kk_take.mp3 w_kk.json kk medium
python3 timing.py; python3 sfx.py ru; python3 sfx.py kk
SKIP_SFX=1 ./build.sh ru     # ~19 min recording
LANG_Q=kk node snap.js out 3 30 60   # preview frames
```
