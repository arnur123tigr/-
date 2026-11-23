# Сен әлемді төңкеріліп көресің / Ты видишь мир вверх ногами (3D glass cutaway of the eye)

Vertical reel 1080x1920, 30 fps, RU ~90 s, KZ ~94 s. Three.js scene (glass eyeball cut in half, coloured cut faces of the
three layers, rays drawn as glowing lines, retina close-up with rods and cones) rendered at 720x1280 with anti-aliasing and
scaled up; 2D scenes (brain, Stratton's goggles, blind-spot test, ENT quiz) and the JAS EDUCATION brand layer at full size.
Code only, no AI images. Voice: Arunur's own cloned ElevenLabs voice «Arnur», eleven_v4, one take per language.

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small    # once per voice take (faster-whisper word times)
python3 words.py vo_kk_take.mp3 w_kk.json kk medium
python3 timing.py                    # vo_<lang>.wav with pauses (+2.6 s quiz pause) + beats.json (captions, scene marks)
./build.sh ru ; ./build.sh kk        # sfx + music (synthesised), record (~35 min), mix (-14 LUFS, voice leads), encode -> koz_<lang>.mp4
LANG_Q=kk node snap.js out 3 10 25   # preview frames
```

Scenes: s1 tree -> inverted image on the retina, s2 ENT trap plaque + the eye is cut in half, s3 layers light up (sclera,
cornea, choroid, retina), s4 rays through pupil and lens cross -> small inverted tree, s5 rods (~120 mln) and cones (~6–7 mln),
s6 brain turns the picture + Stratton 1896–1897 with prism goggles, s7 blind-spot self-test (the dot stays on screen so the
test works), s8 ENT quiz with a 3-2-1 timer, s9 tree turns upright + link in the profile header, end card.

ҰБТ fix (KZ): after `timing.py`, the two «ҰБТ» spots in vo_kk.wav (7.00–7.64 s «ҰБТ-да», 74.64–75.62 s «ҰБТ сұрағы»)
are replaced with Arnur-voice clips from /mnt/project-files/animation/common/ubt_kk_parts/ (ubt_da.mp3, ubt_surag.mp3),
fitted to the same length (atempo, 12 ms crossfades), so the video timing is unchanged. Re-running timing.py undoes it.
