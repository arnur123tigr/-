"""Replaces the call-to-action sentence of the voiceover takes with a re-voiced one (keyword «95»).

  vo_<lang>_take.mp3   full ElevenLabs take (its CTA sentence still says «тарих»)
  cta95_<lang>.mp3     the re-voiced sentence: RU «Напиши «девяносто пять» в комментариях.»
                                               KK «Пікірге «тоқсан бес» деп жаз.»
  -> vo_<lang>_raw.wav take with the sentence swapped (48 kHz mono), input of words.py and timing.py
Usage: python3 splice.py
"""
import subprocess, wave
import numpy as np

SR = 48000
# span = times inside the first and the last word of the old CTA sentence of the take; pre / post = pause before and after the new one
JOBS = {'ru': dict(span=(37.0, 38.4), pre=0.33, post=0.32), 'kk': dict(span=(45.6, 46.66), pre=0.60, post=0.62)}


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


def active_rms(a):
    e, w = env_db(a, .02); n = int(.02 * SR); m = len(a) // n
    fr = a[:m * n].reshape(m, n)[e > -40]
    return float(np.sqrt((fr ** 2).mean()))


def fade(x, fin, fout):
    x = x.copy(); i = int(fin * SR); o = int(fout * SR)
    if i: x[:i] *= np.linspace(0, 1, i) ** 2
    if o: x[-o:] *= np.linspace(1, 0, o) ** 2
    return x


def splice(lang, span, pre, post):
    take = load(f'vo_{lang}_take.mp3'); clip = load(f'cta95_{lang}.mp3')
    R = runs(take)
    k0, k1 = (min(range(len(R)), key=lambda i: 0 if R[i][0] <= t <= R[i][1] else min(abs(t - R[i][0]), abs(t - R[i][1]))) for t in span)
    prev_end, old0, old1, next0 = R[k0 - 1][1], R[k0][0], R[k1][1], R[k1 + 1][0]
    C = runs(clip, min_sil=0.4); c0, c1 = C[0][0], C[-1][1]
    near = np.concatenate([take[int((prev_end - 3.0) * SR):int(prev_end * SR)], take[int(next0 * SR):int((next0 + 3.0) * SR)]])
    gain = active_rms(near) / active_rms(clip[int(c0 * SR):int(c1 * SR)])
    head = fade(take[:int((prev_end + .08) * SR)], 0, .03)
    new = fade(clip[int(max(0, c0 - .03) * SR):int((c1 + .12) * SR)] * gain, .004 if c0 < .03 else .02, .06)
    lead = min(.03, c0)
    tail = fade(take[int((next0 - .05) * SR):], .02, 0)
    z = lambda s: np.zeros(max(0, int(s * SR)), np.float32)
    out = np.concatenate([head, z(pre - .08 - lead), new, z(post - .12 - .05), tail])
    with wave.open(f'vo_{lang}_raw.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    t_new = len(head) / SR + max(0, pre - .08 - lead) + lead
    print(f'{lang}: old sentence {old0:.2f}-{old1:.2f} (pause before {old0 - prev_end:.2f}, after {next0 - old1:.2f}); '
          f'new speech {c1 - c0:.2f}s at {t_new:.2f}-{t_new + c1 - c0:.2f}, gain {20 * np.log10(gain):+.1f} dB; '
          f'take {len(take) / SR:.2f}s -> {len(out) / SR:.2f}s')


if __name__ == '__main__':
    for lang, j in JOBS.items(): splice(lang, **j)
