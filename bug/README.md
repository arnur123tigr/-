# Алғашқы баг шын қоңыз болған / Первый баг был настоящим жуком (Comic)

Vertical reel (1080x1920, 30 fps), KZ ~87 s and RU ~89 s, batch 10 script №4. Comic style drawn in code (thick ink outlines,
halftone dots, yellow / blue / red, SFX bursts), JAS EDUCATION layer: big logo top right, navy end card, link-in-header CTA.
Scene 5 (tweezers pull the moth out of relay #70) is a Higgsfield film shot: Nano Banana Pro still -> Kling 3.0, 5 s
(clips/s5_image.png, clips/s5.mp4; frames: `ffmpeg -i clips/s5.mp4 -vf "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -q:v 3 clips/s5/f_%04d.jpg`, count in clips/s5/count.json). Without clips/s5/count.json the scene falls back to a code-drawn macro.

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small; python3 words.py vo_kk_take.mp3 w_kk.json kk medium   # whisper word times
python3 timing.py                     # vo_<lang>.wav with scene pauses + 3 s quiz pause + «ой!» beat, beats.json
python3 sfx.py ru; python3 sfx.py kk  # comic SFX (zap, buzz, relay clicks, boing, tape) + light upbeat bed
SKIP_SFX=1 ./build.sh ru              # record (~10 min), mix (-14 LUFS, voice leads), encode -> bug_ru.mp4 (with music)
LANG_Q=kk node snap.js out 3 10 25    # preview frames
```

Voice: Arunur's own cloned ElevenLabs voice «Arnur» (eleven_v4, one take per language), ҰБТ written «Ұ-Бе-Те».
Logbook text follows the real Harvard Mark II log page of 9 Sep 1947 («1545 Relay #70 Panel F (moth) in relay. First actual case of bug being found.»),
kept at the Smithsonian National Museum of American History. Edison used «bugs» for faults in an 1878 letter.
