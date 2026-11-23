# Гендер есте сақтаған аштық / «Голод, который запомнили гены» — chalkboard reel

Batch 10, script 13. Vertical 1080x1920, 30 fps, KZ ~93 s and RU ~92 s. Epigenetics told through the Dutch Hunger Winter 1944–45:
chalk on a dark-green board, one Higgsfield film shot (Amsterdam queue, scene 3) that turns into a chalk drawing, ENT quiz with
a 3-second countdown, JAS EDUCATION logo (120 px, top-right) and a navy end card with the link-in-profile CTA.

```
SKIP_RECORD=1 ./build.sh kk   # sound only, reuses video_silent_kk.mp4
LANG_Q=kk node record.js video_silent_kk.mp4 30
./build.sh kk                 # -> epigen_kk.mp4
LANG_Q=ru node snap.js 16 40  # preview stills -> stills/
```

| File | What it does |
|---|---|
| `scene.html` | Whole picture, async `render(T)`, `?lang=kk|ru`. Texts: `TX` table. Engine from `abai/` |
| `timing.py` | Stretches the quiz pause to 3 s, writes `vo_<lang>.wav` + `timeline_<lang>.json` (cuts + marks) |
| `sfx.py` | Synthesised chalk, wind/steps, clock, piano with muted keys, ticks, dings + calm minor music bed |
| `flat.html` | Flat Vector version (JAS navy/amber, flat characters, animated DNA). `FLAT=1 SKIP_RECORD=1 V=flat_silent OUT=epigen_flat ./build.sh kk` after `PAGE=flat.html LANG_Q=kk node record.js flat_silent_kk.mp4 30` |
| `clip/` | Higgsfield shot as JPG frames (`f0001..f0121`, not in repo), `sketch.png` (chalk version of the last frame), `info.json` |

Voice: ElevenLabs eleven_v4, Arunur's own cloned voice «Arnur», one take per language. Voice files are not in the repo.
Film shot: Higgsfield Nano Banana image (2 credits) + Kling 3.0 pro 5 s, no sound (8.75 credits). Fonts: Caveat, Montserrat (OFL).
