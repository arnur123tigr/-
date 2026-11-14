# Align one continuous Kazakh VO take (ElevenLabs) to the per-shot script (kk_segments.json):
# whisper word timestamps -> segment boundaries by word count -> tmap_kk.json and vo_kk_raw.wav (gaps padded per shot).
# usage: python3 -I align_kk.py vo_take.mp3
import json, re, subprocess, sys, os, wave, numpy as np
from faster_whisper import WhisperModel
here = os.path.dirname(os.path.abspath(__file__)); src = sys.argv[1]
segs = json.load(open(os.path.join(here, 'kk_segments.json')))
html = open(os.path.join(here, 'scene.html')).read()
shots = [(float(a), float(b)) for a, b in re.findall(r"^ \[(\d+\.\d+), (\d+\.\d+), '", html, re.M)]
SR = 24000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
a16 = audio[::3] if SR == 48000 else np.interp(np.arange(0, len(audio), SR / 16000), np.arange(len(audio)), audio).astype(np.float32)
m = WhisperModel('small', compute_type='int8')
words = [w for s in m.transcribe(a16, language='kk', word_timestamps=True)[0] for w in s.words]
print('whisper words', len(words))
# cut times: script char fraction -> time where whisper's cumulative char fraction matches, snapped to the quietest spot nearby
env = np.convolve(np.abs(audio), np.ones(480) / 480, 'same')
def quiet(t0, t1):
    i0, i1 = int(max(0, t0) * SR), int(t1 * SR); return (i0 + int(np.argmin(env[i0:i1]))) / SR
# map script chars to whisper chars with difflib, then to time
import difflib
norm = lambda t: re.sub(r"[^а-яёәөұүқғңһіa-z0-9]", "", t.lower())
wchars, wtime = [], []
for w in words:
    n = norm(w.word)
    for j, ch in enumerate(n): wchars.append(ch); wtime.append(w.start + (w.end - w.start) * (j + .5) / max(1, len(n)))
wstr = ''.join(wchars)
sstr = ''; starts = []
for x in segs: starts.append(len(sstr)); sstr += norm(x.replace('Ұ-Бе-Те', 'ҰБТ'))
sm = difflib.SequenceMatcher(None, sstr, wstr, autojunk=False)
pts = [(bl.a + k, bl.b + k) for bl in sm.get_matching_blocks() for k in range(bl.size)]
sa = np.array([p[0] for p in pts]); wb = np.array([p[1] for p in pts])
def s2t(i):
    j = float(np.interp(i, sa, wb)); j0 = int(np.clip(np.floor(j), 0, len(wtime) - 1)); j1 = min(len(wtime) - 1, j0 + 1)
    return wtime[j0] + (wtime[j1] - wtime[j0]) * (j - j0)
cuts = [0.0]
for k in range(1, len(segs)):
    t = (s2t(starts[k] - 0.5) + s2t(starts[k])) / 2 if starts[k] > 0 else 0
    fw = norm(segs[k].split()[0])[:3] if segs[k] else ''
    cand = [w for w in words if fw and norm(w.word)[:3] == fw and abs(w.start - t) < 1.5]
    if cand: w = min(cand, key=lambda w: abs(w.start - t)); t = w.start - 0.08; cuts.append(quiet(t - 0.25, t + 0.05)); continue
    cuts.append(quiet(t - 0.3, t + 0.3))
OVERRIDE = json.loads(os.environ.get('CUTS', '{}'))  # manual fixes: {"shot": seconds in the take}
for k, v in OVERRIDE.items(): cuts[int(k)] = quiet(v - 0.25, v + 0.05)
end = len(audio) / SR
# resolve None (empty segs) and build per-shot clips
clips = []; prev = 0.0; voiced = [i for i, s in enumerate(segs) if s]
bounds = {}
vc = [c for i, c in enumerate(cuts) if segs[i]]
for n, i in enumerate(voiced):
    s0 = vc[n]; s1 = vc[n + 1] if n + 1 < len(voiced) else end
    bounds[i] = (s0, s1)
MIN = {4: 2.8, 43: 2.0, 50: 0.8, 54: 3.4, 10: 7.0, 37: 9.0}
out = []; tmap = []; A = 0.0
for i, (a, b) in enumerate(shots):
    if i in bounds:
        s0, s1 = bounds[i]; clip = audio[int(s0 * SR):int(s1 * SR)]
        L = max(len(clip) / SR + 0.1, MIN.get(i, 1.8))
        out.append((A, clip))
    else:
        L = MIN.get(i, b - a)
    tmap.append([round(A, 3), round(A + L, 3), a, b]); print(f'{i:2d} RU {b - a:5.2f} KZ {L:5.2f} {segs[i][:40]}')
    A += L
buf = np.zeros(int(A * SR) + SR)
for t, clip in out: s = int(t * SR); buf[s:s + len(clip)] += clip
s16 = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
with wave.open(os.path.join(here, 'vo_kk_raw.wav'), 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s16.tobytes())
json.dump({'dur': round(A, 3), 'map': tmap}, open(os.path.join(here, 'tmap_kk.json'), 'w'))
print('total', round(A, 2), 'take', round(end, 2))
