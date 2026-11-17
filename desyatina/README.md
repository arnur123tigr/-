# «17 миллион десятина: жер қалай кетті»

Reel about the resettlement policy and the Stolypin reform in numbers, RU and KZ, 1080x1920, 30 fps.
Style: dark 3D "money" studio (Three.js glossy black floor, gold numbers, glass spheres), map scenes on a NASA Blue Marble satellite plane
with Kazakhstan (Baikonur filled) outlined in amber. JAS EDUCATION brand: logo top-right, navy end card, CTA "link in the profile header".

| Scene | Picture |
|---|---|
| 1 | 17 000 000 odometer |
| 2 | satellite map: 185 000 km² = almost all of Kyrgyzstan dropped into Kazakhstan |
| 3 | 1861 / 1868 gold plates, 30 desyatinas, archive photo (Kansk resettlement point, 1899) |
| 4 | Transsib drawn over the satellite map, settlers piling up at Petropavl and Omsk |
| 5 | Stolypin portrait in a glass sphere, 1.5 million settlers |
| 6 | kibitka tax coins 1.5 → 3 → 4 rub., red rising chart |
| 7 | Akhmet Baitursynuly portrait (1913) and his quote |
| 8 | three numbers to remember, end card |

Voices (ElevenLabs eleven_v4): RU Egor, KZ Ерсұлтан. Takes: vo_ru_take.mp3, vo_kk_take.mp3.

Photos (public domain, Wikimedia Commons): photos/settlers.jpg crop of "Переселенческий пункт близ ст. Канск" (I. R. Tomaszkiewicz, 1899),
photos/stolypin.jpg "Stolypin.jpg" (c. 1908), photos/baitursynov.jpg "Ахмет Байтұрсынұлы (1913-02-02).jpg".

## Build
```
python3 prep_map.py      # geo.json (needs data/adm0.geojson, Natural Earth 10m admin 0)
python3 prep_tex.py      # tex/sat.jpg (needs ../../data/C1.jpg, NASA BMNG tile C1)
python3 timing.py        # beats.json
LANG_Q=ru node record.js video_silent_ru.mp4 30
LANG_Q=kk node record.js video_silent_kk.mp4 30
python3 sfx.py ru; python3 mix.py ru; python3 sfx.py kk; python3 mix.py kk
./build.sh               # desyatina_{ru,kk}.mp4 and *_no_music.mp4
```
