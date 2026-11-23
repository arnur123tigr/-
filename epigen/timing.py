"""Stretch the three quiz pauses in the voice take to exactly 3 s and write
vo_<lang>.wav + timeline_<lang>.json (scene cuts and marks in final time)."""
import json, subprocess, sys, numpy as np, wave
SR = 48000
CFG = {
 'kk': dict(pauses=[(80.54, 82.63)],
            cuts=[6.95, 15.0, 21.1, 30.5, 43.0, 57.4, 72.2, 84.6],
            marks={'dna': 3.94, 'how': 6.16, 'ubt': 9.04, 'winter': 12.62, 'war': 18.8, 'food': 19.26,
                   'kcal': 23.14, 'less': 25.56, 'preg': 28.24, 'born': 30.68, 'watch': 33.2, 'ill': 38.4, 'why': 42.46,
                   'meth': 45.96, 'off': 48.96, 'letters': 50.18, 'piano': 53.62, 'keys': 55.7,
                   'y2008': 57.62, 'sixty': 63.52, 'grand': 64.74, 'rev': 68.36,
                   'qa': 76.54, 'qb': 77.94, 'qc': 78.9, 'ans': 82.63, 'cta': 84.76}),
 'ru': dict(pauses=[(79.63, 81.27)],
            cuts=[6.6, 14.7, 21.75, 30.0, 41.85, 55.9, 70.85, 83.0],
            marks={'dna': 3.18, 'how': 5.96, 'ubt': 8.74, 'winter': 12.18, 'war': 18.84, 'food': 19.76,
                   'kcal': 22.9, 'less': 25.32, 'preg': 27.1, 'born': 30.26, 'watch': 32.82, 'ill': 37.28, 'why': 40.92,
                   'meth': 44.82, 'off': 48.3, 'letters': 49.58, 'piano': 52.3, 'keys': 54.42,
                   'y2008': 55.92, 'sixty': 61.94, 'grand': 63.42, 'rev': 67.2,
                   'qa': 75.56, 'qb': 77.3, 'qc': 78.3, 'ans': 81.27, 'cta': 83.22}),
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
