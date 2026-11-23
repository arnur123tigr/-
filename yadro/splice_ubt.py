"""Swap every spoken «ҰБТ» in the Kazakh take for one correctly voiced clip, keeping the take's length (so the video stays in sync).
Usage: python3 splice_ubt.py   (reads vo_kk_take_orig.mp3 + the shared clips, writes vo_kk_take.mp3)
Each whole word with its ending is replaced: «ҰБТ-да» and «ҰБТ сұрағы» (clips made in Arnur's voice by the UBT thread)."""
import subprocess, sys, numpy as np, wave, io
SR = 48000
P = '/mnt/project-files/animation/common/ubt_kk_parts/'
SEGS = [(11.05, 11.72, P + 'ubt_da.mp3'), (74.40, 75.90, P + 'ubt_surag.mp3')]   # take times from word times + energy dips
def load(p):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).copy()
take = load('vo_kk_take_orig.mp3')
def trim(clip):
    idx = np.where(np.abs(clip) > .03 * np.abs(clip).max())[0]; return clip[max(0, idx[0] - int(.01 * SR)): idx[-1] + int(.03 * SR)]
rms = lambda x: np.sqrt((x ** 2).mean() + 1e-12)
out = take.copy()
for a, b, cp in SEGS:
    clip = trim(load(cp))
    i0, i1 = int(a * SR), int(b * SR); n = i1 - i0
    ctx = np.concatenate([take[i0 - int(.6 * SR):i0], take[i1:i1 + int(.6 * SR)]]); ctx = ctx[np.abs(ctx) > 1e-3]
    ratio = len(clip) / n
    c = clip
    if ratio > 1.0:                # longer than the gap: speed up a little (pitch kept); shorter: silence after it
        r = min(ratio, 1.3)
        p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={r:.4f}', '-f', 'f32le', '-'], input=clip.tobytes(), capture_output=True, check=True).stdout
        c = np.frombuffer(p, np.float32).copy()
    c = c[:n] if len(c) >= n else np.concatenate([c, np.zeros(n - len(c), np.float32)])
    c *= rms(ctx) / rms(c[np.abs(c) > 1e-3])
    f = int(.012 * SR); w = np.linspace(0, 1, f)
    tail = np.zeros(n); tail[-f:] = 1   # crossfade only at the start and into the old audio at the very end
    seg = c.copy(); seg[:f] = seg[:f] * w + take[i0:i0 + f] * (1 - w); seg[-f:] = seg[-f:] * w[::-1] + take[i1 - f:i1] * (1 - w[::-1])
    out[i0:i1] = seg
    print(f'ҰБТ {a:.2f}-{b:.2f} s: clip {len(clip) / SR:.2f} s -> gap {n / SR:.2f} s (tempo x{ratio:.2f})')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-b:a', '192k', 'vo_kk_take.mp3'], input=out.tobytes(), check=True)
