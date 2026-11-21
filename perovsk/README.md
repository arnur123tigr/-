# Перовск: қаланы жаулаған генералдың атымен атады (Flat Vector timeline)

Vertical reel (1080x1920, 30 fps), KZ and RU. Flat Vector look from the script (navy #1D2B53, turquoise, yellow, coral, cream; flat shapes, one-tone shadow, pop & slide), JAS brand layer: bigger logo top right (120 px; navy on cream scenes), navy end card with amber CTA (link in profile header only).

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small   # whisper word times (once per take; same for kk)
python3 timing.py                                    # vo_<lang>.wav with scene pauses + 2.2 s quiz pause, beats.json
python3 sfx.py ru; python3 sfx.py kk                 # pops, cannon, hooves, quiz ticks + D-minor ambient bed
./build.sh ru                                        # record (~1.5 min), mix (-14 LUFS, voice leads), encode -> perovsk_ru.mp4
LANG_Q=kk node snap.js out 3 10 25                   # preview frames
```

Scenes: 1 cream gate, sign «Қызылорда» slips and shows «Перовск»; 2 Ақмешіт fortress on the Syr Darya; 3 siege of 1853 (cannons, cracks, portrait overlay); 4 sign rewritten Ақмешіт > Форт Перовский > Перовск 1867; 5 Жанқожа with riders 1856; 6 1922 Ақмешіт, 1925 Қызылорда, gate turns turquoise, overview of all names; 7 ҰБТ quiz with 3-2-1 timer; 8 gate again with ghost «Перовск», arrow to profile header.

Voices: ElevenLabs eleven_v4, one take each, tag "[serious, clear documentary narrator, calm, with short dramatic pauses]": KZ Aruzhan (1047 credits, 67.2 s), RU Alina (1085 credits, 69.0 s). Years spelled in words; ҰБТ written «Ұ-Бе-Те», ЕНТ «Е-Эн-Тэ», RU reads «Акмешит».
