# «Artificial» — OpenAI-дің 5 күні (KZ, montage-collage)

Personal project of Arunur (not JAS): neutral look, no logo, the script's own comment CTA.

- `scene.html` — the whole reel as code, deterministic `render(T)`, 1080×1920; scenes timed to `beats.json`.
- `script_kk.txt` + `timing.py` — caption chunks / scene beats aligned to whisper word times (`words.py` → `words_kk.json`).
- `vo_kk_take.mp3` (ElevenLabs Ерсұлтан, one take), `vo_end_take.mp3` («Пікіріңді жаз.»), `tighten.py` (shorter pauses, ×1.04) → `vo_kk.mp3`.
- Photos: Wikimedia Commons 960px thumbs (`fetch_photos.sh`, `slow_fetch.sh`), X posts via api.fxtwitter.com; `cutouts.py` (rembg) → `cut/`.
- `ai/` — 2 Higgsfield stills (video call, empty cinema). `tex/wc.jpg` — NASA Blue Marble (public domain).
- `clips/<name>/f_0001.jpg…` + `index.json` — optional video excerpts (trailer, DevDay, APEC); without them a still is shown.
- `./build.sh` → `out/openai_kk.mp4` (cues → `sfx.py` synth effects + music → `mix.py` → record → mux).
