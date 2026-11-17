# Бес жыл «қырғыз» болдық: 1917–1936 (Minimal Line timeline)

Vertical reel (1080x1920, 30 fps), KZ 73.9 s and RU 68.3 s. Thin white lines on dark navy, one accent colour (turquoise #4FD1C5) as the script asks; JAS EDUCATION brand layer: logo top right, navy end card with amber CTA.

```
python3 timing.py                    # once after a new voice take: vo_<lang>.wav + beats.json (needs w_<lang>.json from words.py)
python3 sfx.py ru; python3 sfx.py kk # line sounds + calm ambient bed (run one at a time)
SKIP_SFX=1 ./build.sh ru             # record (~8 min), mix (-14 LUFS, voice leads), encode -> kyrgyz_ru.mp4 + _no_music
LANG_Q=kk node snap.js out 3 10 25   # preview frames
```

| File | What |
|---|---|
| scene.html | one long world: time axis at y=1080, camera keyframes (`camKeys`), 7 points, line icons (flag, building that falls apart, stamp, name frames, mountains, capital pin), photo overlays, ҰБТ card, arrow, captions, end card. Texts per language in `L` |
| timing.py | caption script (`display=spoken`, `@marks`), aligned to whisper word times, short pause before each scene |
| sfx.py / mix.py / build.sh | sound and final encode |
| photos/ | alash_1913.jpg = Commons «Baitursynuly, Bokeikhan and Dulatuly.jpg» (1913, PD); kyzylorda_1926.jpg = Commons «Деятели партии «Алаш».jpg» (Kzyl-Orda 1926, Kyzylorda museum, PD), printed caption painted out |

Voices: ElevenLabs eleven_v4, one take each: KZ Aruzhan, RU Alina, tag "[clear, confident, moderately fast teacher]". Years spelled out in words; АКСР/КСР written as letters (А-Ка-Эс-Эр).
No photo of the 1925 government building in Kyzylorda exists on Wikimedia, so scene 5 uses the 1926 Kyzylorda group photo.
