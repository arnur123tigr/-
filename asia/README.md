# Регионы Азии — переделка в новом стиле JAS (RU)
Новая сцена на 2D-движке (спутниковая карта, светящиеся регионы, плашки стран, большой логотип).
Голос: старый дубль Egor из первой версии + новая общая концовка `../_shared/cta_link_ru.mp3` (ссылка в шапке профиля), без новых трат на всю озвучку.
Сборка: `python3 prep.py && python3 words.py vo_ru.mp3 words_ru.json ru small && python3 beats.py && python3 ../_shared/caps.py && ./build.sh` → `out/asia_ru.mp4`.
Данные: NASA Blue Marble, Natural Earth 10m (public domain).
