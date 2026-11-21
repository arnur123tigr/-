# Орыс хан — атасы қазақ хандарының (Flat Vector + satellite map)

Vertical reel (1080x1920, 30 fps), KZ ~66 s and RU ~69 s, batch 9 script №1. Flat Vector in the script's palette
(navy #1D2B53, turquoise #2EC4B6, yellow #FFD23F, coral #EF476F, cream #FFF3D6): flat shapes, no outlines, one-tone shadow, «pop & slide».
Scene 2 (Ақ Орда, Сығанақ on the Syr Darya) is a satellite "from space" map, as the project rule asks for every map.
JAS EDUCATION layer: bigger logo top right (120 px, navy on cream scenes), navy end card with amber CTA (link in profile header only).

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small; python3 words.py vo_kk_take.mp3 w_kk.json kk medium   # whisper word times
python3 timing.py                     # vo_<lang>.wav with scene pauses + 3 s quiz pause, beats.json (marks + captions)
python3 sfx.py ru; python3 sfx.py kk  # pops / whooshes / knocks + light upbeat bed (synthesised)
SKIP_SFX=1 ./build.sh ru              # record (~10 min), mix (-14 LUFS, voice leads), encode -> orys_ru.mp4 (with music)
LANG_Q=kk node snap.js out 3 10 25    # preview frames
```

| File | What |
|---|---|
| scene.html | all 8 scenes: crown + «ОРЫС», satellite map (tex/world.jpg + tex/ca.jpg NASA Blue Marble, KZ border from shapes.json, Syr Darya from syr.json = Natural Earth 10m), flat khan character (Turkic robe, fur-rim crown), arrows Тоқтамыс / Әмір Темір, family tree, name tag, ҰБТ card + polaroid photo, quiz with donut timer, loop ending |
| timing.py | caption script (`*word` = yellow, `display=spoken`, `@marks`), aligned to whisper; splits whisper's glued «Орысхан» |
| photos/monument.jpg | optional polaroid photo in scene 6 (Kerei & Zhanibek monument): Commons «KZ-2015-500tenge-Khanate-b.png» (National Bank coin «550 years of the Kazakh Khanate», 2015, public domain; it shows the Astana monument), 330 px thumb upscaled 2x |

Voices: ElevenLabs eleven_v4, one take each, tag "[clear, confident, moderately fast teacher, with a light intrigue]": KZ Aruzhan (899 credits), RU Alina (882 credits).
Sygnak coordinates 44.157 N, 66.961 E (ru.wikipedia). Genealogy per the script (Tarikh-i Rashidi): Orys → Bolat → Kerei; Orys → Kuyrshyk → Barak → Zhanibek.
