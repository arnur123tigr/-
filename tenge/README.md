# tenge — «Теңге құпия операциясы, 1993» / «Секретная операция «тенге», 1993» (KZ + RU)
Batch 10, script 15. Flat Vector in the script's «secret» palette (#1D2B53, #FFD23F, #2EC4B6, #EF476F) + two satellite map scenes (MAPS RULE), JAS brand (corner logo 122 px, end card, link-in-profile CTA). 1080x1920, code only.
Scenes: secret suitcase → calendar to 15 November 1993 (ENT date) → satellite map: 1991 independence, soviet ruble, 1993 new ruble from Moscow, old rubles flood in, prices rise →
four artists design the tenge → satellite map: sketch to London, Harrison & Sons, planes with secret crates back to Almaty → scales 1 ₸ = 500 roubles + real 1993 banknotes →
National Currency Day, silver «теңге» coin → ENT quiz with a spinning coin timer → suitcase opens, link in profile header → JAS end card.

- Engine: `engine.js`, `helpers.js`, `record.js` and the flat kit from baikonur/; `scene.html?lang=ru|kk` (deterministic `render(t)`).
- Map: `tex/world.jpg`, `tex/ca.jpg`, `shapes.json` (NASA Blue Marble, Natural Earth).
- Voice: Arunur's own cloned ElevenLabs voice «Arnur» (eleven_v4, one take per language) → `vo_<lang>_raw.mp3`; `stretch.py` makes the quiz pause 3.3 s → `vo_<lang>.mp3`.
- Timing: `words.py` (faster-whisper; kk with `medium`) → `words_<lang>_raw.json`; `beats.py` → `beats.json`, `caps_<lang>.json` (ALT/OVR handle whisper's spellings).
- Sound: `sfx.py` (synth SFX + 92 bpm minor «detective» bed), `mix.py` (voice-first). `./build.sh ru|kk` → `out/tenge_<lang>.mp4`.
- Photos (`photos/`): Commons «Kazakhstan-1993-Bill-{1,10,20,100}-Obverse.jpg», National Bank of Kazakhstan, public domain. upload.wikimedia.org answered 429 to the cloud; 10/20/100 were downloaded on Arunur's laptop and staged.
