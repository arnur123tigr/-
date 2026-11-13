# Kazakh VO with free Microsoft Edge neural voice (kk-KZ-DauletNeural), one clip per shot.
# Builds vo_kk.wav and tmap_kk.json: per shot [A, B, a, b] = KZ interval -> RU animation interval.
# usage: python3 make_kk.py [voice] [rate]
import json, re, subprocess, sys, wave, numpy as np, os
voice = sys.argv[1] if len(sys.argv) > 1 else 'kk-KZ-DauletNeural'; rate = sys.argv[2] if len(sys.argv) > 2 else '+8%'
here = os.path.dirname(os.path.abspath(__file__))
segs = json.load(open(os.path.join(here, 'kk_segments.json')))
html = open(os.path.join(here, 'scene.html')).read()
shots = [(float(a), float(b)) for a, b in re.findall(r"^ \[(\d+\.\d+), (\d+\.\d+), '", html, re.M)]
assert len(shots) == len(segs), (len(shots), len(segs))
SR = 24000
def synth(text):
    subprocess.run([sys.executable, os.path.join(here, 'etts.py'), voice, text, '/tmp/_seg.mp3', rate], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '/tmp/_seg.mp3', '-ac', '1', '-ar', str(SR), '/tmp/_seg.wav'], check=True)
    w = wave.open('/tmp/_seg.wav'); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    nz = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, nz[0] - 200): nz[-1] + 400] if len(nz) else np.zeros(0)
MIN = {4: 2.8, 43: 2.0, 50: 0.8, 54: 3.4, 10: 7.0, 37: 9.0}
GAP = 0.35
vo = []; tmap = []; A = 0.0
for i, ((a, b), text) in enumerate(zip(shots, segs)):
    clip = synth(text) if text else np.zeros(0)
    d = len(clip) / SR
    L = max(d + GAP, MIN.get(i, 1.8)) if text else MIN.get(i, b - a)
    lead = 0.12 if text else 0
    start = int((A + lead) * SR)
    vo.append((start, clip))
    tmap.append([round(A, 3), round(A + L, 3), a, b])
    print(f'{i:2d} RU {b - a:5.2f}s  KZ {L:5.2f}s  voice {d:5.2f}s  {text[:40]}')
    A += L
total = A
buf = np.zeros(int(total * SR) + SR)
for s, clip in vo: buf[s:s + len(clip)] += clip
s16 = (np.clip(buf / (np.abs(buf).max() + 1e-9) * 0.9, -1, 1) * 32767).astype(np.int16)
with wave.open(os.path.join(here, 'vo_kk_raw.wav'), 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s16.tobytes())
json.dump({'dur': round(total, 3), 'map': tmap}, open(os.path.join(here, 'tmap_kk.json'), 'w'))
print('total', round(total, 2))
