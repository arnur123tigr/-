"""Replaces each «ҰБТ» in the Kazakh voice (vo_kk.wav, already timed) with one correctly voiced clip, without moving anything else.
The clip is fitted into the same window (sped up a little if longer, centred with silence if shorter), so picture and captions stay in sync.
Usage: python3 splice_ubt.py /mnt/project-files/animation/common/ubt_kk_parts   (keeps vo_kk_orig.wav as the untouched copy)
The parts folder holds «ҰБТ» said in context (ubt_da = «ҰБТ-да», ubt_surag = «ҰБТ сұрағы», ...); each window takes the whole phrase."""
import json, subprocess, sys, os, wave
import numpy as np

SR = 48000
# windows in the RAW take (vo_kk_take.mp3), from its energy envelope: the whole «ҰБТ-да» and the whole «ҰБТ сұрағы»
RAW = [(11.45, 12.20, 'ubt_da.mp3'), (69.93, 70.88, 'ubt_surag.mp3')]
B = json.load(open('beats.json'))['kk']; OFF = B['off']


def raw_to_file(x):                                          # raw take time -> time in vo_kk.wav (video time minus OFF)
    shift = 0.
    for c, g in B['cuts']:                                   # cut times are video times (OFF + raw + earlier gaps)
        if c - OFF - shift <= x: shift += g
    return x + shift


def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


src = 'vo_kk_orig.wav' if os.path.exists('vo_kk_orig.wav') else 'vo_kk.wav'
if src == 'vo_kk.wav': os.rename('vo_kk.wav', 'vo_kk_orig.wav'); src = 'vo_kk_orig.wav'
a = load(src).copy()
rms = lambda x: np.sqrt((x ** 2).mean() + 1e-12)
for r0, r1, name in RAW:
    clip = load(os.path.join(sys.argv[1], name))
    nz = np.where(np.abs(clip) > .01)[0]; clip = clip[max(0, nz[0] - 240):nz[-1] + 480]   # trim silence
    f0, f1 = raw_to_file(r0), raw_to_file(r1); i0, i1 = int(f0 * SR), int(f1 * SR); n = i1 - i0
    c = clip
    if len(c) > n:                                           # speed up to fit (pitch kept)
        tempo = min(1.35, len(c) / n)
        tmp = 'ubt_tmp.wav'
        with wave.open(tmp, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(c, -1, 1) * 32767).astype(np.int16).tobytes())
        c = load_t = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', tmp, '-af', f'atempo={tempo:.4f}', '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
        c = np.frombuffer(c, np.int16).astype(np.float32) / 32768; os.remove(tmp)
    c = c * (rms(a[i0:i1][np.abs(a[i0:i1]) > .01]) / rms(c[np.abs(c) > .01]))   # match the loudness of what it replaces
    if len(c) > n: c = c[:n]
    seg = np.zeros(n, np.float32); p = (n - len(c)) // 2; seg[p:p + len(c)] = c
    fd = int(.008 * SR); seg[:fd] *= np.linspace(0, 1, fd); seg[-fd:] *= np.linspace(1, 0, fd)
    a[i0:i1] = seg
    print(f'ҰБТ raw {r0:.2f}-{r1:.2f} -> file {f0:.2f}-{f1:.2f} (video {f0 + OFF:.2f}), window {n / SR:.2f} s, clip {len(clip) / SR:.2f} s')
with wave.open('vo_kk.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
