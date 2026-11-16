"""Stretch the three quiz pauses in the voice take to exactly 3 s and write
vo_<lang>.wav + timeline_<lang>.json (scene cuts and marks in final time)."""
import json, subprocess, sys, numpy as np, wave
SR = 48000
CFG = {
 'ru': dict(pauses=[(12.80, 13.79), (25.94, 27.02), (39.02, 40.07)],
            cuts=[3.5, 6.2, None, 18.6, None, 33.3, None, 44.5],
            marks={'o1a': 10.64, 'o1b': 11.42, 'o1c': 12.26, 'o2a': 23.24, 'o2b': 24.02, 'o2c': 25.36,
                   'nick': 15.56, 'father': 28.54, 'home': 30.80, 'eq': 41.10, 'ent': 44.72, 'cta': 47.34}),
 'kk': dict(pauses=[(12.26, 13.47), (25.27, 26.64), (37.79, 39.21)],
            cuts=[2.95, 5.7, None, 18.3, None, 33.1, None, 43.3],
            marks={'o1a': 9.78, 'o1b': 10.32, 'o1c': 11.20, 'o2a': 22.26, 'o2b': 22.92, 'o2c': 24.12,
                   'nick': 15.40, 'father': 28.08, 'home': 30.58, 'eq': 39.82, 'ent': 43.56, 'cta': 46.00}),
}
QUIZ = 3.0      # length of each pause in the final video
TAIL = 2.4      # end card after the last word
lang = sys.argv[1]; c = CFG[lang]
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'vo_{lang}_take.mp3', '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
segs, pos, shift, T = [], 0.0, [], 0.0
extra = []
for (p0, p1) in c['pauses']:
    mid = (p0 + p1) / 2
    segs.append(a[int(pos * SR):int(mid * SR)])
    add = QUIZ - (p1 - p0)
    segs.append(np.zeros(int(add * SR), np.float32))
    extra.append((mid, add)); pos = mid
segs.append(a[int(pos * SR):])
out = np.concatenate(segs)
def nt(t):  # original time -> final time
    return t + sum(add for (m, add) in extra if t > m)
voend = len(out) / SR
dur = round(voend + TAIL, 2)
out = np.concatenate([out, np.zeros(int((dur - voend) * SR) + SR, np.float32)])
with wave.open(f'vo_{lang}.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
# scene cuts: question scenes end when the 3-second pause ends
qend = [nt(p0) + QUIZ for (p0, p1) in c['pauses']]
qstart = [nt(p0) for (p0, p1) in c['pauses']]
cuts = []; k = 0
for x in c['cuts']:
    if x is None: cuts.append(round(qend[k] - 0.05, 2)); k += 1
    else: cuts.append(round(nt(x), 2))
ids = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9']
b = [0] + cuts + [dur]
scenes = [{'id': ids[i], 'start': b[i], 'end': b[i + 1]} for i in range(9)]
marks = {k: round(nt(v), 2) for k, v in c['marks'].items()}
for i, q in enumerate(qstart): marks[f'q{i+1}'] = round(q, 2)
marks['voend'] = round(voend, 2)
json.dump({'lang': lang, 'dur': dur, 'scenes': scenes, 'marks': marks}, open(f'timeline_{lang}.json', 'w'), ensure_ascii=False, indent=1)
print(lang, dur, [(s['id'], s['start']) for s in scenes], marks)
