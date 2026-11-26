# esil — «Есілдің суы мұхитқа құяды» / «Вода Есиля течёт в океан» (KZ + RU)
Batch of 26.11.2026, script 1. A drop goes from Astana down the Esil, into the Irtysh (the Irtysh starts in the Altai in China, through Lake Zaysan),
into the Ob at Khanty-Mansiysk and through the Ob Gulf into the Kara Sea (Arctic Ocean). Twist: the Irtysh (4 248 km) is longer than the Ob (3 650 km) but is its tributary.
ҰБТ/ЕНТ in frame 11 (Irtysh, Esil, Tobol = Arctic basin), CTA = link in the profile header. GEO-KARTA script, code only, JAS EDUCATION brand, 1080x1920 30 fps.

- Engine: satellite globe from `tyn/` (<- kulja/ <- kaganat/): `scene.html?lang=kk|ru`, deterministic `render(t)`, `record.js`, `snap.js`.
- Map: `tex/world.jpg`, `tex/main.jpg`, `dem.bin` from tyn/; `tex/detail.jpg` = the route lon 60..90, lat 45..74, 100 px/deg; `tex/city.jpg` = Astana lon 69..74, lat 50..52.5, 240 px/deg
  (`fetch_data.sh` + `prep_map.py`: NASA Blue Marble NG C1, Mapzen Terrarium relief). `shapes.json`: Natural Earth 10m borders, Kazakhstan, rivers merged into ordered
  source -> mouth lines (Esil, Irtysh, Ob + a hand-drawn line down the Ob Gulf, Tobol; Syr Darya, Ural, Ile in grey), Lake Zaysan.
- Voice: Arunur's ElevenLabs voice «Arnur» (eleven_v4, one take per language). `SLOT=51.06,51.70 python3 prep_vo.py kk` splices the approved «ҰБТ-да» clip; `python3 prep_vo.py ru`.
  `words.py` (faster-whisper medium) -> `w_<lang>.json`; `timing.py` -> `vo_<lang>.wav`, `beats.json`.
- Sound: `sfx.py` (synth effects + music bed), `mix.py` (voice-led mix, -14 LUFS). Build: `./build.sh kk|ru` -> `esil_<lang>.mp4`.
- Facts (script sources): Irtysh 4 248 km, Ob 3 650 km (Wikipedia); Esil and Tobol are left tributaries of the Irtysh (Geography 20, 21).
