# bosqyn — «Миллион қазақ шекарадан қашты» / «Миллион казахов бежали за границу» (KZ + RU)
The famine of 1931–1933 and the exodus of about a million Kazakhs (China, Mongolia, Iran, Afghanistan, neighbouring republics).
Batch 11 GEO-KARTA script №2, ~98 s (KZ) / ~92 s (RU), 1080x1920 30 fps, JAS EDUCATION brand, dark satellite globe.
Code only: Arunur chose no Higgsfield, so frames 3 (mother at the empty yurt, 1932) and 10 (the same woman on a Tian Shan pass) are painted panels in canvas.

- Engine: copied from `kulja/` (<- semey/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language, `vo_*_take.mp3`). `prep_vo.py` splices the approved «ҰБТ-да» clip
  (`animation/common/ubt_kk_parts/ubt_da.mp3`) into the KZ take and shortens long pauses; `words.py` (faster-whisper medium) -> `w_<lang>.json`;
  `timing.py` (captions markup + beats) -> `vo_<lang>.wav`, `beats.json`. RU text has ЕНТ written «Е Эн Тэ».
- Sound: `sfx.py` (synth effects + quiet minor music bed with a flute), `mix.py` (voice-led, -14 LUFS). Build: `./build.sh kk|ru` -> `bosqyn_<lang>.mp4`.
- Photo: F. Goloshchekin, Wikimedia Commons «Filipp Goloshchyokin.jpg», public domain (`img/`).
- Facts (script sources): Wikipedia «Голод в Казахстане (1930—1933)» (livestock ~40 M -> ~4.5 M; ~1.03 M left, ~616 k did not return; 1.5–2.3 M dead);
  censuses 1926 (58 %) and 1939 (38 %); 31 May = day of memory of the victims of political repression and famine. Routes on the map are approximate.
