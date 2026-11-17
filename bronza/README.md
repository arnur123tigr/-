# 3000 жыл бұрынғы шахта: қола қалай туды (PS2 low-poly 3D cutaway)

Vertical reel 1080x1920, 30 fps, RU ~52.8 s and KZ ~54.6 s. Three.js scene rendered at 486x864 without anti-aliasing and scaled up
(bloom + light scanlines = PS2 look). JAS EDUCATION brand layer: navy/amber pills and plaques, logo top right, end card.
Code only, no AI images. Real museum photos as overlays (scene 4 dagger, scene 6 pot).

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small   # once per voice take (faster-whisper word times)
python3 words.py vo_kk_take.mp3 w_kk.json kk medium
python3 timing.py                    # vo_<lang>.wav with pauses + beats.json (captions, scene marks)
python3 sfx.py ru; python3 sfx.py kk # synthesised effects + steppe music bed
SKIP_SFX=1 ./build.sh ru             # record (~10 min), mix (-14 LUFS, voice leads), encode -> bronza_ru.mp4 + _no_music
LANG_Q=kk node snap.js out 3 10 25   # preview frames
```

| File | What |
|---|---|
| scene.html | 7 scenes: s1 steppe with ≈500 pits, s2 cutaway mine (layers, malachite, adit, miners with baskets, torches), s3 furnace in a cut with bellows and °C gauge, s4 copper + tin = bronze, casting the axe, real dagger card, s5 mine grows + peak chart, s6 Andronovo settlement (semi-dugouts, cattle pen, two-wheeled chariot), s7 ENT plaque + axe flies to the profile header. Texts in table `TX` (RU/KZ) |
| timing.py | caption script (`display=spoken`, `@marks`), pauses before scenes |
| sfx.py / mix.py / build.sh | sound and final encode |
| photos/ | museum photos + credits.json (shown small on screen) |

Voices: ElevenLabs eleven_v4, one take each: RU Egor (young, energetic), KZ Ерсұлтан.
