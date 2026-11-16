# Противоположности в географии (remake, RU, CTA «гео»)
Remake of a screen-recorded IG reel ("Everything in geography has an opposite"), satellite-map look, 1080x1920, 51 s. Voice: ElevenLabs Egor (energetic), one take (`vo_take.mp3`).
Same engine in `britain/` (the "Great Britain / UK / England" remake, 69.6 s).

- `scene.html` + `engine.js`: 2D canvas, deterministic `render(t)`; camera keys in `CAMK`, voice times wrapped in `V()` (voice starts at 0.3 s).
- `tex/`: NASA Blue Marble NG (July, topo+bathy, public domain) crops, regraded to the teal ocean of the reference (`prep_tex.py`, `grade.py`; sources downloaded to /home/user/data).
- `shapes.json`: Natural Earth 10m outlines (`prep_shapes.py`). `cards/`: procedural relief cards (`cards.py`).
- Build: `node record.js video_silent.mp4 30`, `python3 sfx.py` (cues.json), `python3 mix.py <name>` (voice leads the bed by ~17 dB median), then mux with ffmpeg.
