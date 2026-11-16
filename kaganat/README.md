# Тюркский каганат: от Алтая до Чёрного моря

Vertical map story (1080x1920, 30 fps) in two languages: Russian (47.0 s) and Kazakh (54.0 s). A dark satellite globe of Eurasia:
the lands of the Turks glow turquoise, the Rouran are dull red, the Silk Road is a golden line, the split of 603 leaves the east
turquoise and the west blue. Text, numbers, panels, logo and the end card follow the JAS EDUCATION style guide
(`references/STYLE_GUIDE.md`, pull request #26: navy `#130B54`, amber `#FEB300`, white; red-orange `#E8502F` only for the enemy and for loss).

The reel ends with a call to follow the link in the profile header or in the description. The comment keyword («95») was dropped on
2026-11-16: the Russian files were rebuilt and delivered again; the Kazakh files delivered before that still carry the keyword ending
of the first commit, because only the Russian version was asked for.

Everything is drawn by code. `render(T)` in `scene.html` is deterministic, so the video is recorded frame by frame in headless Chromium.

## Build

```
./build.sh ru        # -> kaganat_ru.mp4, kaganat_ru_no_music.mp4
./build.sh kk        # -> kaganat_kk.mp4, kaganat_kk_no_music.mp4
SKIP_RECORD=1 ./build.sh ru     # sound and final encode only, reuses video_silent_ru.mp4
```

Needs node with Playwright (Chromium), ffmpeg, python3 with numpy. Without a GPU a frame takes 1.3 s (about half an hour per language;
two languages can be recorded at the same time). The voice files are not in the repository, rebuild them once before the first build:
`python3 splice.py && python3 timing.py`.

Quick preview frames: `LANG_Q=kk node snap.js out_dir 3.4 15.4 38.5`.

## Files

| File | What it does |
|---|---|
| `scene.html` | The whole picture: a Three.js globe (NASA texture, relief, atmosphere) under a 2D canvas with fills, labels, counters, captions, the call to action and the end card. `?lang=ru` or `?lang=kk` |
| `beats.json` | Timing for both languages: caption words with their times, named beats, scene cuts. Written by `timing.py`, read by the scene and by the sound scripts, so picture and sound follow the same marks |
| `timing.py` | The script of the voiceover with caption and beat markup. Aligns it to the word times (`w_<lang>.json`), inserts the pauses, writes `vo_<lang>.wav` and `beats.json` |
| `splice.py` | Cuts the "write the keyword in the comments" sentence out of the full takes (`vo_<lang>_take.mp3`), so that the voice ends with the link sentence alone |
| `words.py` | Word timestamps of a voice file (faster-whisper), only needed after a new voice take. The committed `w_<lang>.json` come from the takes before the cut: the words of the cut sentence were taken out and the later ones moved up, so the scenes before it keep their timing |
| `sfx.py` | Synthesised effects and the music bed |
| `mix.py` | The mix: the voice is evened out and leads, effects and music are ducked under it, -14 LUFS. Prints by how many dB the voice leads while the narrator speaks |
| `record.js`, `snap.js` | Recording of the silent video and single preview frames |
| `prep_map.py`, `fetch_data.sh` | Rebuild `tex/`, `dem.bin` and `shapes.json` from the sources (only when the map itself has to change) |
| `brand/`, `fonts/`, `vendor/` | The logo, Inter and Inter Tight (OFL), three.js r170 |

## Where to change things

- Colours: `BR` and `C` at the top of the script in `scene.html`. The map layer uses `C.turk`, `C.rouran`, `C.blue`; everything else uses the brand's `C.acc`.
- Texts on screen: the `L` table in `scene.html`. Voiceover text, captions and pauses: `SCRIPT` in `timing.py`.
- Call to action: only the link in the profile header or in the description, no comment keyword. Picture: `cta()` and `endCard()` in `scene.html`, texts `L.go`, `L.where`, `L.or`, `L.endA`, `L.endB`.
- Territories and the Silk Road: the hand-placed outlines in `prep_map.py` (`python3 prep_map.py vec` rewrites `shapes.json`). Borders of the sixth century are approximate.

## Sources

- Satellite picture: NASA Blue Marble Next Generation (July, topography and bathymetry), public domain.
- Coastline, lakes, borders, the Huang He: Natural Earth, public domain.
- Relief: Mapzen Terrain Tiles (AWS Open Data, Terrarium encoding). They contain SRTM and GMTED2010 data courtesy of the U.S. Geological Survey
  and ETOPO1 data courtesy of the U.S. National Oceanic and Atmospheric Administration; Europe terrain data produced using Copernicus data and
  information funded by the European Union (EU-DEM layers); ArcticDEM terrain data DEM(s) were created from DigitalGlobe, Inc., imagery and
  funded under National Science Foundation awards 1043681, 1559691, and 1542736.
- Voices: ElevenLabs (RU Egor, KZ Ерсұлтан), one take per language.
- Fonts: Inter and Inter Tight, SIL Open Font License.
