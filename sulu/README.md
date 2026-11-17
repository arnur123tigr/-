# Сулу-каган «Сүзеген» / «Бодливый»: comic panels over a satellite map

Vertical reel 1080x1920, 30 fps, RU 57.8 s and KZ 64.8 s. Comic style (ink frames, halftone dots, sound-word bursts, narration boxes, black silhouettes with amber rim light) layered over a real satellite map of Zhetysu (NASA Blue Marble NG, public domain). JAS EDUCATION brand layer: amber/navy boxes, logo top right, navy end card. CTA: link in the profile header only. Code only, no Higgsfield.

```
python3 words.py vo_ru_take.mp3 w_ru.json ru small; python3 words.py vo_kk_take.mp3 w_kk.json kk medium   # whisper word times
python3 timing.py                     # vo_<lang>.wav (pauses before scenes) + beats.json (captions, marks)
python3 sfx.py ru; python3 sfx.py kk  # synthesised comic SFX + epic drum bed (one language at a time)
SKIP_SFX=1 ./build.sh ru              # record (~12 min), mix (-14 LUFS, voice leads), encode -> sulu_ru.mp4 + sulu_ru_no_music.mp4
LANG_Q=kk ./sheet.sh 1 13 20 27       # contact sheet of preview frames -> /tmp/claude-0/sheet.jpg
```

| File | What |
|---|---|
| scene.html | 7 scenes (`S1..S7`), texts in `T` (RU/KZ), comic kit (panel, halftone, boom, letters, capBox), silhouettes as SVG paths (`PATHS`), map engine (2D, from britain/) |
| tex/ | Blue Marble crops (`prep_tex.py` from britain/, `grade.py`): z = lon 50..100 lat 25..58 @64 px/deg, z2 = lon 66..86 lat 39..48 @200 px/deg |
| shapes.json | `prep_shapes.py`: Natural Earth rivers and borders; Chu and Talas traced by hand; approximate Turgesh khaganate outline |
| photos/ | Taraz citadel ruins, Turkestan Album 1871–72 (Commons «Aulie-ata Razvaliny citadeli.jpg», PD); Turgesh coin (Commons, CNG Coins, CC BY-SA 3.0); square-hole coins from Kyrgyzstan (Commons «Sogdian coins - Carpatic 01.jpg», PD), credited on screen |

Voices: ElevenLabs eleven_v4, one take each, tag "[energetic, dramatic movie-trailer narrator]": RU Egor (young, energetic), KZ Ерсұлтан.
Commons has no free photo of Ak-Beshim (Suyab), so scene 2 uses the script's alternative, the Taraz ruins.
