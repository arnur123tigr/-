# Долли қойының үш анасы болған / У овечки Долли было три матери (Flat Vector + 1 film shot)

Vertical reel (1080x1920, 30 fps), KZ ~82 s and RU ~81 s, batch 10 script №6. Flat Vector in the script's palette
(navy #1D2B53, turquoise #2EC4B6, yellow #FFD23F, coral #EF476F, cream #FFF3D6). Scene 6 is a Higgsfield film shot
(Nano Banana Pro still + Kling 3.0 5 s motion, sound off) of a white-faced lamb and a Scottish Blackface ewe.
JAS EDUCATION layer: big logo top right (120 px), navy end card with amber CTA (link in profile header only).
Voice: Arunur's own ElevenLabs clone «Arnur» (eleven_v4, one take per language). `female/` keeps the unused first takes (Aruzhan / Alina).

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small; python3 words.py vo_kk_take.mp3 w_kk.json kk medium   # whisper word times
python3 timing.py                     # vo_<lang>.wav with scene pauses + 3 s quiz pause, beats.json (marks + captions)
python3 sfx.py ru; python3 sfx.py kk  # pops, «бее», zap, pipette + light upbeat bed (synthesised)
SKIP_SFX=1 ./build.sh ru              # record, mix (-14 LUFS, voice leads), encode -> dolly_ru.mp4 (with music)
LANG_Q=kk node snap.js out 3 10 25    # preview frames
```

| File | What |
|---|---|
| scene.html | 9 scenes: sheep + 3 hearts / crossed father, ear tag DOLLY 1996, mother №1 (white face) gives the udder cell and its nucleus (DNA), mother №2 (Blackface) gives the egg, pipette removes its nucleus, DNA goes in, electric zap, division 1-2-4-8 into mother №3, 277 dots -> 1, film shot 05.07.1996, «who does Dolly look like», quiz with a yarn-ball timer, everybody hops + arrow up |
| hf/ | still.jpg (Higgsfield image), clip.mp4; frames f_###.jpg (24 fps) made with `ffmpeg -i hf/clip.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -q:v 3 hf/f_%03d.jpg`, loaded by `prep(T)` before each frame; the clip plays at real speed and ends with the scene |
| vo_kk_take_raw.mp3 | original KZ take; vo_kk_take.mp3 has a 0.4 s blip in the quiz pause (67.6-68.3 s) muted |

Facts per the script: Roslin Institute, born 5 July 1996, 1 success out of 277 attempts, nucleus from a Finn Dorset (white face) udder cell, egg and surrogate Scottish Blackface.
