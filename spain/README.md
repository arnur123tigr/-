# spain remake (RU only, CTA «ссылка в шапке профиля»)
Remake of a screen-recorded English IG geography reel («Spain has the strangest borders») in the JAS EDUCATION satellite-map style, 1080x1920, ~91 s.
Voice: ElevenLabs Egor energetic (eleven_v4), one take (`vo_ru.mp3`). Engine = `caspian/` 2D Blue Marble canvas; corner logo enlarged to 122 px (Arunur, 2026-11-18).
`prep_tex.py tex iberia -14 8 26 48 240` + `grade.py`, `prep_shapes.py` (Natural Earth 10m: Spain, Llívia, Ceuta, Melilla, Gibraltar, Andorra, France, Portugal, Morocco, UK),
`beats.py` -> beats.json + caps_ru.json, `./build.sh` -> `out/spain_ru.mp4`. Pheasant Island, Andorra vs Almaty and Peñón de Vélez are drawn panels.
