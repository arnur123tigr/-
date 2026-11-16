# Абайдың шын аты / «Абая звали не Абай» — chalkboard quiz

Vertical quiz reel (1080x1920, 30 fps), KZ 55.7 s and RU 57.6 s. Chalk on a dark-green board, three questions with a real 3-second
countdown each, real public-domain photos taped into the chalk frames, JAS EDUCATION logo top-right and a navy end card.

```
./build.sh kk      # -> abai_kk.mp4, abai_kk_no_music.mp4
./build.sh ru
SKIP_RECORD=1 ./build.sh kk   # sound only, reuses video_silent_kk.mp4
LANG_Q=ru node snap.js 10 16.5   # preview frames -> stills/
```

| File | What it does |
|---|---|
| `scene.html` | Whole picture, `render(T)`, `?lang=kk|ru`. Texts on screen: `TX` table |
| `timing.py` | Stretches the three quiz pauses in the voice take to exactly 3 s, writes `vo_<lang>.wav` and `timeline_<lang>.json` (scene cuts + marks) |
| `sfx.py` | Synthesised chalk, ticks, dings, rag wipes and a light study music bed |
| `words.py` | Word times of a voice take (faster-whisper), used to set the marks in `timing.py` |
| `record.js`, `snap.js` | Frame recording / preview stills |

Voices: ElevenLabs eleven_v4, one take each: KZ "Aruzhan kaz" (661 credits), RU "Alina" (696 credits). Voice files are not in the repo.

Photos (`photos/`, Wikimedia Commons, public domain): Abai (File:Abai_Kunanbaev.jpg, Semey 1896 group photo, cropped),
Shokan Valikhanov in uniform (File:Chokan_Valikhanov_portrait.jpg, before 1865), Ybyrai Altynsarin (File:Altynsarin.jpg). Sepia baked in.
Fonts: Caveat and Montserrat (OFL).
