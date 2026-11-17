"""Sound mix for the reel: voice + effects (+ music) -> mix_<lang>.wav and mix_<lang>_no_music.wav (48 kHz, -14 LUFS).
The voice is first brought to one loudness and its sharpest peaks are held back, so both languages sit the same; effects and
music are ducked under it (sidechain). The report at the end shows by how many dB the voice leads everything else while the narrator speaks.
Usage: python3 mix.py ru|kk"""
import json, os, re, subprocess, sys, tempfile, wave
import numpy as np

LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
DUR = json.load(open('beats.json'))[LANG]['end']
OFF = .30                       # the voice starts this late in the video (OFF in timing.py)
TARGET, CEIL = -14.0, -1.5      # loudness of the result (LUFS) and its peak ceiling (dBFS)
VOICE, MUSIC, SFX = -18.0, -30.0, -7.0   # voice and music: loudness before the master (LUFS); effects: plain gain (dB), their track is peak-normalised
VLIM = 'alimiter=limit=-6.5dB:attack=3:release=70:level=false'   # the voice is spiky (peaks 23 dB over its loudness): a limiter evens it out and keeps the phrasing
SRC = [f'vo_{LANG}.wav', f'sfx_{LANG}.wav', f'music_{LANG}.wav']


def ff(*a):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-y', *a], capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-2000:])
    return r.stderr
def loud(path):                 # integrated loudness (LUFS) and sample peak (dBFS)
    e = ff('-i', path, '-af', 'ebur128=peak=sample', '-f', 'null', '-')
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', e)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', e)[-1])
def read(path):
    with wave.open(path) as w: return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
dB = lambda x: 20 * np.log10(np.maximum(x, 1e-7))

VG = VOICE - loud(SRC[0])[0]; MG = MUSIC - loud(SRC[2])[0]
_t = os.path.join(tempfile.mkdtemp(), 'v.wav'); ff('-i', SRC[0], '-af', f'aresample=48000,highpass=f=75,volume={VG:.2f}dB,{VLIM}', '-c:a', 'pcm_f32le', _t)
VT = VOICE - loud(_t)[0]        # what the limiter took from the loudness is given back


def graph(music, what, gain, limit=True):
    """what: all | voice | bed (the last two are for the report only)."""
    v = (f'[0:a]aresample=48000,highpass=f=75,volume={VG:.2f}dB,{VLIM},volume={VT:.2f}dB,'
         f'adelay={int(OFF * 1000)}:all=1,apad=whole_dur={DUR},atrim=0:{DUR},asplit=3[v][k1][k2]')
    s = f'[1:a]aresample=48000,volume={SFX:.2f}dB[s];[s][k1]sidechaincompress=threshold=-24dB:ratio=3:attack=8:release=250[sd]'
    m = f'[2:a]aresample=48000,volume={MG if music else -150:.2f}dB[m];[m][k2]sidechaincompress=threshold=-26dB:ratio=4:attack=15:release=500[md]'
    o = {'all': '[v][sd][md]amix=inputs=3:normalize=0:duration=first', 'voice': '[sd]anullsink;[md]anullsink;[v]anull',
         'bed': '[v]anullsink;[sd][md]amix=inputs=2:normalize=0:duration=first'}[what]
    return f'{v};{s};{m};{o},volume={gain:.2f}dB' + (f',alimiter=limit={CEIL}dB:attack=3:release=60:level=false' if limit else '') + '[o]'
def render(music, what, gain, out, limit=True):
    ff(*[x for p in SRC for x in ('-i', p)], '-filter_complex', graph(music, what, gain, limit), '-map', '[o]', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', out)


tmp = tempfile.mkdtemp()
for music, name in ((1, f'mix_{LANG}.wav'), (0, f'mix_{LANG}_no_music.wav')):
    t = os.path.join(tmp, 'm.wav'); gain = 0.
    render(music, 'all', -12, t, False); gain = TARGET - (loud(t)[0] + 12)            # measured 12 dB down, so nothing clips on the way
    for _ in range(2): render(music, 'all', gain, name); gain += TARGET - loud(name)[0]   # the limiter takes a little loudness: correct for it
    render(music, 'all', gain, name); I, pk = loud(name)
    # how far the voice leads: voice and everything else rendered apart with the same settings, compared in 0.4 s windows
    # (whole band, and 300-4000 Hz, where speech is understood: a low boom there costs the voice nothing)
    render(music, 'voice', gain, os.path.join(tmp, 'v.wav'), False); render(music, 'bed', gain, os.path.join(tmp, 'b.wav'), False)
    v, b = read(os.path.join(tmp, 'v.wav')), read(os.path.join(tmp, 'b.wav')); n = int(.4 * 48000); hop = n // 2
    def levels(x, band=None):
        if band: X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / 48000); X[(f < band[0]) | (f > band[1])] = 0; x = np.fft.irfft(X, len(x))
        return dB(np.array([np.sqrt((x[i:i + n] ** 2).mean()) for i in range(0, len(x) - n, hop)]))
    lv, lb = levels(v), levels(b); on = lv > np.median(lv[lv > -40]) - 8; lead = (lv - lb)[on]; sp = (levels(v, (300, 4000)) - levels(b, (300, 4000)))[on]
    tm = (np.arange(len(lv)) * hop / 48000)[on]; worst = sorted(np.argsort(lead)[:4])
    print(f'{name}: {I:.1f} LUFS, peak {pk:.1f} dBFS, master {gain:+.1f} dB | voice gain {VG + VT:+.1f} dB' + (f', music gain {MG:+.1f} dB' if music else '')
          + f' | while the narrator speaks the voice leads by: median {np.median(lead):.1f} dB, 5% worst {np.percentile(lead, 5):.1f} dB, least {lead.min():.1f} dB ('
          + ', '.join(f'{tm[i]:.1f} s' for i in worst) + f'); in the speech band: median {np.median(sp):.1f} dB, 5% worst {np.percentile(sp, 5):.1f} dB, least {sp.min():.1f} dB')
