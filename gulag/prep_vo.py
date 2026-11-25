"""Usage: python3 prep_vo.py kk|ru [slot_start,slot_end] (ru: step 1 only; kk without a slot: step 1 only, to find the slot). vo_kk_take.mp3 (ElevenLabs, voice «Arnur», one take) -> vo_kk_raw.wav (48 kHz mono):
1) every pause longer than 0.36 s is shortened to 0.30 s (the take was slow: 98.6 s -> 93.1 s);
2) «ҰБТ-да» is replaced by the approved clip animation/common/ubt_kk_parts/ubt_da.mp3 (the clone reads ҰБТ wrongly),
   loudness matched to the word it replaces. SLOT = where the word is in the file after step 1 (found by ear / energy plot).
Then: python3 words.py vo_kk_raw.wav w_kk.json kk medium && python3 timing.py"""
import re, subprocess, sys, wave
import numpy as np
LANG = sys.argv[1] if len(sys.argv) > 1 else 'kk'
SR = 48000; UBT = '/mnt/project-files/animation/common/ubt_kk_parts/ubt_da.mp3'; SLOT = tuple(map(float, sys.argv[2].split(','))) if len(sys.argv) > 2 else None
dec = lambda p: np.frombuffer(subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
a = dec(f'vo_{LANG}_take.mp3')
o = subprocess.run(['ffmpeg', '-hide_banner', '-i', f'vo_{LANG}_take.mp3', '-af', 'silencedetect=noise=-34dB:d=0.36', '-f', 'null', '-'], capture_output=True, text=True).stderr
s = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]; e = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
keep, prev = [], 0
for x, y in zip(s, e):
    if x < .05: prev = max(0, y - .05); continue
    cut = (y - x) - .30
    if cut <= 0: continue
    mid = (x + y) / 2; keep.append((prev, mid - cut / 2)); prev = mid + cut / 2
keep.append((prev, len(a) / SR))
f = int(.006 * SR); parts = []
for x, y in keep:
    p = a[int(x * SR):int(y * SR)].copy(); p[:f] *= np.linspace(0, 1, f); p[-f:] *= np.linspace(1, 0, f); parts.append(p)
a = np.concatenate(parts)
if LANG == 'kk' and SLOT:
  c = dec(UBT); env = np.array([np.sqrt((c[i:i + 480] ** 2).mean()) for i in range(0, len(c) - 480, 480)]); on = np.where(env > env.max() * .03)[0]
  c = c[on[0] * 480:(on[-1] + 2) * 480]; i0, i1 = int(SLOT[0] * SR), int(SLOT[1] * SR)
  rms = lambda x: np.sqrt((x ** 2).mean()); c = c * rms(a[i0:i1]) / rms(c); g = int(.008 * SR); c[:g] *= np.linspace(0, 1, g); c[-g:] *= np.linspace(1, 0, g)
  a = np.concatenate([a[:i0], c, np.zeros(int(.03 * SR), np.float32), a[i1:]])
out = a
with wave.open(f'vo_{LANG}_raw.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print(f'vo_{LANG}_raw.wav', round(len(out) / SR, 2), 's')
