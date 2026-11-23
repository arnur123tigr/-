# Баланың жынысын әке анықтайды / Пол ребёнка определяет отец (Minimal Line)

Vertical reel (1080x1920, 30 fps), batch 10 script 9. Thin black lines on white paper, X chromosomes turquoise, Y coral; JAS EDUCATION brand: navy logo top right (120 px), navy end card with amber CTA (link in the profile header).

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small; python3 words.py vo_kk_take.mp3 w_kk.json kk medium
python3 timing.py                    # vo_<lang>.wav (pauses before scenes, 3 s quiz pause) + beats.json
python3 sfx.py ru; python3 sfx.py kk # effects + calm ambient bed
SKIP_SFX=1 ./build.sh ru             # record, mix (-14 LUFS, voice leads), encode -> sexchrom_ru.mp4
LANG_Q=kk node snap.js out 5 20 40   # preview frames
```

Scenes (scene.html): crown + six wives; cell «КІМ?» + ҰБТ pill; XX / XY columns; Punnett 2x2 grid with gametes; big Y with blinking SRY, two roads, 50/50 bar; hen ZZ/ZW and crocodile with nest and thermometer; crown with Y + rolling die; quiz А/Ә/Б with 3 s timer; X and Y shake hands, arrow up, end card.

Voice: Arunur's own cloned ElevenLabs voice «Arnur», eleven_v4, one take per language. X/Y written «икс»/«игрек», SRY «Эс-Эр-Уай», ZW «зэт-вэ», ҰБТ «Ұ-Бе-Те», ЕНТ «Е-Эн-Тэ».
