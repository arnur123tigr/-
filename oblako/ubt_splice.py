"""KZ only: the voice read «ҰБТ-да» wrongly, so the approved clip common/ubt_kk_parts/ubt_da.mp3 replaces raw 74.51-75.12 s of vo_kk_raw.wav
(RMS-matched, short fades). w_kk.json is already shifted for the 0.11 s the clip adds. Run once right after vo_kk_raw.wav is made (build.sh does)."""
import subprocess, wave, sys
import numpy as np
SR, S, E = 48000, 74.51, 75.12
CLIP = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/animation/common/ubt_kk_parts/ubt_da.mp3'
rd = lambda *a: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', *a, '-ar', '48000', '-ac', '1', '-f', 's16le', '-'], capture_output=True).stdout, np.int16) / 32768.
a, c = rd('-i', 'vo_kk_raw.wav'), rd('-i', CLIP)
env = np.abs(c) > .01; i0 = np.argmax(env); i1 = len(c) - np.argmax(env[::-1]); c = c[max(0, i0 - 240):i1 + 480]
rms = lambda x: np.sqrt((x[np.abs(x) > .01] ** 2).mean())
c = c * rms(a[int(S * SR):int(E * SR)]) / rms(c); f = int(.008 * SR); c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
out = np.concatenate([a[:int(S * SR)], c, a[int(E * SR):]])
with wave.open('vo_kk_raw.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print('ҰБТ-да spliced', round(len(c) / SR, 3), 's')
