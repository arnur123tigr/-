# Исатай мен Махамбет: POV, 16-bit pixel art

Vertical reel (1080x1920, 30 fps), RU 58.7 s and KZ 62.9 s. Everything is drawn by code at 270x480 and shown x4 (nearest neighbour), so it looks like an old 16-bit game. JAS EDUCATION brand: navy/amber HUD panels, logo top right, end card.

```
python3 timing.py                    # once after a new voice take: vo_<lang>.wav + beats.json
python3 sfx.py ru; python3 sfx.py kk # 8-bit effects + chiptune bed (run one at a time)
SKIP_SFX=1 ./build.sh ru             # record (~2 min), mix (-14 LUFS, voice leads), encode -> isatai_ru.mp4 + _no_music
LANG_Q=kk node snap.js out 3 10 25   # preview frames
```

| File | What |
|---|---|
| scene.html | all 8 scenes (`SC.s1..s8`), HUD texts in table `L` (RU/KZ), photo cards, captions, end card |
| timing.py | caption script (`display=spoken`, `@marks`), alignment to whisper word times, pauses before scenes |
| sfx.py / mix.py / build.sh | sound and final encode |
| photos/ | Жәңгір хан (Commons «Jangir-Kerei-khan.png», PD), Махамбет (ru.wikipedia «Utemisov_Mahambet.jpg», PD-old-70), monument in Atyrau (Commons, AyanaS83, CC BY-SA 3.0, credited on screen) |
| fonts/ | Press Start 2P (OFL, has all Kazakh letters), Montserrat (OFL) |

Voices: ElevenLabs eleven_v4, one take each: RU Egor (young, energetic), KZ Ерсұлтан.
