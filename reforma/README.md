# Как казахскую степь разрезали на части (реформы 1822–1868)

Vertical map story, 1080x1920, 30 fps, Russian (63.7 s) and Kazakh (68.4 s). An old parchment map (sepia relief, seas with engraved
ripple lines, ink rivers, dotted deserts) where red ink draws the six oblasts of 1867–1868, wax seals stamp them, and the JAS EDUCATION
brand layer (navy and amber pills, captions, logo, end card) sits on top. Real public-domain pictures: M. Speransky (engraving by Gedan),
Alexander II (photo, 1874), J. Arrowsmith's map of Central Asia (1872), all from Wikimedia Commons.

## Build

```
python3 prep_map.py        # only when the map changes (needs ./fetch_data.sh first): tex/ and shapes.json
python3 timing.py          # beats.json from the sentence times of the two voice takes
./build.sh ru ; ./build.sh kk
```

Frames: `LANG_Q=kk node snap.js out 3.5 18 30` (one frame ~0.5 s, the whole reel ~20 min per language).

## Files

| File | What it does |
|---|---|
| `scene.html` | The picture, `render(T)`, `?lang=ru|kk`. Texts in `L`, colours in `BR` / `C` |
| `timing.py` | Voice sentences with their times, caption chunks and colour marks, named beats -> `beats.json` |
| `prep_map.py` | Parchment base, archive overlay warp, portraits, oblast shapes |
| `sfx.py`, `sfxlib.py` | Synth effects (paper, seals, pen, crown, steps, coins) and the music bed |
| `mix.py` | Voice first: -14 LUFS, effects and music ducked under the voice |

Oblast borders are approximate (built from modern regions). Sources: Natural Earth (public domain), Mapzen Terrain Tiles (AWS Open Data;
SRTM/GMTED2010 courtesy of USGS, ETOPO1 courtesy of NOAA), Wikimedia Commons public-domain images, ElevenLabs voices (RU Egor, KZ Ерсұлтан),
PT Serif / Montserrat / Inter (OFL).
