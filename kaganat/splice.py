"""Cuts the "write the keyword in the comments" sentence out of the voiceover takes, so that the call to action is the link sentence alone.

  vo_<lang>_take.mp3   full ElevenLabs take. Its ending: «... 552-603 годы. Напиши «тарих» в комментариях. За полной подготовкой
                       перейдите по ссылке в шапке профиля или в описании.» (KK: «... жылдар. Пікірге «тарих» деп жаз. Толық дайындық үшін ...»)
  -> vo_<lang>_raw.wav the take without the comment sentence (48 kHz mono), input of words.py and timing.py
Usage: python3 splice.py
"""
import subprocess, wave
import numpy as np

SR = 48000
# span = times inside the first and the last word of the sentence to cut; pause = silence left between its neighbours
JOBS = {'ru': dict(span=(37.0, 38.4), pause=0.35), 'kk': dict(span=(45.6, 46.66), pause=0.65)}


def load(p):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def env_db(a, w=0.005):
    n = int(w * SR); m = len(a) // n
    return 20 * np.log10(np.sqrt((a[:m * n].reshape(m, n) ** 2).mean(1)) + 1e-9), w


def runs(a, thr=-42.0, min_sil=0.15):
    """Speech runs [(t0, t1)] separated by silences of at least min_sil seconds."""
    e, w = env_db(a); on = e > thr; out = []; i = 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and (on[j] or not on[j:j + int(min_sil / w)].sum() == 0): j += 1
            out.append((i * w, j * w)); i = j
        else: i += 1
    return out


def fade(x, fin, fout):
    x = x.copy(); i = int(fin * SR); o = int(fout * SR)
    if i: x[:i] *= np.linspace(0, 1, i) ** 2
    if o: x[-o:] *= np.linspace(1, 0, o) ** 2
    return x


def cut(lang, span, pause):
    take = load(f'vo_{lang}_take.mp3')
    R = runs(take)
    k0, k1 = (min(range(len(R)), key=lambda i: 0 if R[i][0] <= t <= R[i][1] else min(abs(t - R[i][0]), abs(t - R[i][1]))) for t in span)
    prev_end, old0, old1, next0 = R[k0 - 1][1], R[k0][0], R[k1][1], R[k1 + 1][0]
    head = fade(take[:int((prev_end + .08) * SR)], 0, .03)
    tail = fade(take[int((next0 - .05) * SR):], .02, 0)
    out = np.concatenate([head, np.zeros(max(0, int((pause - .08 - .05) * SR)), np.float32), tail])
    with wave.open(f'vo_{lang}_raw.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f'{lang}: cut {old0:.2f}-{old1:.2f} (pause before {old0 - prev_end:.2f}, after {next0 - old1:.2f}); the next sentence now starts at '
          f'{(len(out) - len(tail)) / SR + .05:.2f} after a pause of {pause:.2f}; take {len(take) / SR:.2f}s -> {len(out) / SR:.2f}s')


if __name__ == '__main__':
    for lang, j in JOBS.items(): cut(lang, **j)
