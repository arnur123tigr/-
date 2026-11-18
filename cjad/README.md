# JAS x CJ promo (2026-11-18)

Vertical 9:16 1080x1920 promo for JAS Education: a CJ-like character (Arunur's generated photos) visits the JAS centre and invites viewers to a trial ЕНТ lesson. RU voice, ElevenLabs "Evgeniy Rybakov" (ws3YyKFd5whKb21yaXES), eleven_v4, one take (570 credits, 27.2 s).

Shots (Higgsfield):
1. Intro, GTA-style follow camera: Nano Banana Pro still (corridor + character) -> Kling 3.0 pro 5 s, no sound.
2. Mirror hall, talking: Arunur's photo as start_image + VO part 1 as audio_references -> Seedance 2.0 std 720p 7 s.
3. Map sofa, talking: Nano Banana Pro still -> Seedance 2.0 std 720p 11 s + VO part 2.
4. Banners sofa, talking: Arunur's photo -> Seedance 2.0 std 720p 10 s + VO part 3.
5. End card (endcard.py), link-in-profile CTA.

`beat.py` synthesises a laid-back hip-hop beat; `build.sh` upscales, cuts each clip to its VO part, adds logo + captions, ducks the beat under the voice.
Clips and VO parts live in /mnt/project-files/animation/cjad/clips/.

    W=<dir with s1-4.mp4, a1-3.mp3, beat.wav> OUT=jas_cj_ru.mp4 INTRO=5.0 MUSIC_DB=-11 ./build.sh
