"""Insert silence into a voice take at the quietest point between two times (the 3 s quiz pause).
Usage: python3 pause.py in.mp3 out.mp3 t_from t_to extra_seconds"""
import sys, subprocess, numpy as np
src, dst, a, b, ex = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:])
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', src, '-f', 's16le', '-ac', '1', '-ar', '44100', '-'], capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32); SR = 44100; n = int(.05 * SR)
i0, i1 = int(a * SR), int(b * SR); e = [np.abs(x[i:i + n]).mean() for i in range(i0, i1 - n, n // 4)]
cut = i0 + int(np.argmin(e)) * (n // 4) + n // 2; print('cut at', cut / SR)
y = np.concatenate([x[:cut], np.zeros(int(ex * SR), np.float32), x[cut:]]).astype(np.int16)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 's16le', '-ar', '44100', '-ac', '1', '-i', '-', '-b:a', '192k', dst], input=y.tobytes(), check=True)
