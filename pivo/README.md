# Адамзаттың алғашқы жазбасы — сыра есебі / Первая запись человечества — учёт пива

Vertical reel (1080x1920, 30 fps), batch 10 script №14. Flat Vector in the script's clay palette (terracotta #C8693B, sand #F2D7A6,
navy #1D2B53, turquoise #2EC4B6) + one Higgsfield film shot (scene 3, Sumerian scribe) + satellite map of Mesopotamia (scene 2, project maps rule).
JAS EDUCATION layer: 120 px logo top right, navy end card with amber CTA (link in profile header only).

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small; python3 words.py vo_kk_take.mp3 w_kk.json kk medium
python3 timing.py [ru|kk]             # vo_<lang>.wav with scene pauses + 3 s quiz pause, beats.json
python3 sfx.py ru; python3 sfx.py kk  # clay taps, beer, wind, waves, keys + light synthesised bed
SKIP_SFX=1 ./build.sh ru              # record, mix (-14 LUFS, voice leads), encode -> pivo_ru.mp4 (with music)
LANG_Q=kk node snap.js out 3 10 25    # preview frames
```

| File | What |
|---|---|
| scene.html | 9 scenes: tablet + beer + barley, satellite Mesopotamia (tex/me.jpg = NASA Blue Marble merge, Tigris/Euphrates from Natural Earth 10m rivers.json), Higgsfield clip (hf/f frames), decoded tablet + Kushim, pictogram → ideogram → cuneiform + hieroglyphs, pile of signs → 22 Phoenician letters + ship, alef → Α → A/А → phone, quiz with hourglass, loop ending |
| hf/s3.png, hf/s3.mp4 | Higgsfield: Nano Banana Pro still (2 credits) + Kling 3.0 Turbo 5 s (7.5 credits); hf/f = 1080x1920 30 fps frames |
| fonts/NotoSans{Cuneiform,EgyptianHieroglyphs,Phoenician}.ttf | Google Fonts (OFL), real cuneiform / hieroglyph / Phoenician glyphs |

Voice: ElevenLabs eleven_v4, Arunur's own cloned voice «Arnur» (dYmt55JYwdFpUMbmVszd), one take per language, tag
"[energetic, witty storyteller with light irony, revealing a funny surprising fact]", ҰБТ written «Ұ-Бе-Те».

Frames of the film shot (not in git): `mkdir -p hf/f && ffmpeg -i hf/s3.mp4 -vf "fps=30,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6" -q:v 3 hf/f/%03d.jpg`
