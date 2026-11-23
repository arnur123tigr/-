"""Timing for the Semey test site reel (456 explosions).

Aligns the script (captions markup below) to the whisper word timestamps of the raw voiceover (w_<lang>.json),
inserts the pauses marked with ^, and writes
  vo_<lang>.wav   voiceover with the pauses inserted (48 kHz mono; video time = this file + OFF seconds)
  beats.json      per language: end, caption words with video times, named beats (word times) and derived cues (S2..S7, Hit, ...)
Markup:  |  caption chunk break     t: r: g: b: n:  word colour (turk, rouran, gold, blue, number)
         @name  beat on the next word     ^0.3  pause of 0.3 s after the previous word     ~ at word end = no space after
Usage: python3 timing.py            (needs vo_<lang>_raw.wav (ffmpeg from vo_<lang>_take.mp3, see build.sh) and w_<lang>.json from words.py)
"""
import json, re, subprocess, difflib, wave
import numpy as np

OFF = 0.35          # the voice starts this late in the video
TAIL = 2.3          # video keeps running after the last word (the end card: logo + call to action)
SCRIPT = {
 'ru': """
@s1 Сорок лет | на нашей земле | прогремели @k456 n:456 | ядерных взрывов. ^0.12 | Но @people остановили их | t:простые t:люди. ^0.20
@s2 @poly Семипалатинский | полигон — | @area n:18,5 n:тысяч | квадратных километров. ^0.08 | Эту историю | нужно знать | и для @ent t:ЕНТ, | и для жизни. ^0.20
@s3 @date n:29 n:августа | n:1949 года | здесь взорвали | первую атомную | бомбу @ussr r:СССР. ^0.20
@s4 Потом взрывы | не прекращались | @y40 n:сорок n:лет. ^0.08 | @k116 n:116 — | на земле | и в воздухе, ^0.04 | @k340 n:340 — | под землёй. ^0.12 | А людей | из @vill ближайших сёл | никто @nomove r:не r:выселял. ^0.20
@s5 По разным оценкам, | от радиации | пострадали | @mil больше n:миллиона | человек. ^0.12 | @sick Росли болезни, | дети рождались | больными. ^0.12 | Но говорить | об этом открыто | было @silent r:нельзя. ^0.24
@s6 Но в @y89 n:1989 году | поэт @olzhas t:Олжас t:Сулейменов | по @tv телевидению | призвал людей | собраться. ^0.08 | Так родилось | движение @nev t:«Невада t:— t:Семей». ^0.08 | @sign Сотни тысяч людей | поставили подписи. ^0.20
@s7 И @closed n:29 n:августа | n:1991 года | полигон @shut t:закрыли. ^0.08 | Ровно через | @d42 n:сорок n:два n:года | после первого взрыва, | день в день. ^0.12 | А @un ООН объявила | этот день | Международным днём | против ядерных испытаний. ^0.24
@s8 Вопрос t:ЕНТ. ^0.08 | В каком году | закрыли | Семипалатинский полигон? ^0.08 | @oA n:1989-й, | @oB n:91-й | @oC или n:93-й? ^2.4 | @ans Правильно: | в g:1991-м, | 29 августа. ^0.20
@s9 Хочешь глубоко знать | историю Казахстана — | @link перейди | по @go g:ссылке | в @bio шапке профиля.
""",
 'kk': """
@s1 Қырық жыл бойы | біздің жерде | @k456 n:456 | ядролық жарылыс болды. ^0.12 | Бірақ оны @people тоқтатқан — | t:қарапайым t:халық. ^0.20
@s2 @poly Семей полигоны — | @area n:18 n:500 | шаршы шақырым. ^0.08 | Бұл @ent t:ҰБТ-да да, | өмірде де | білу керек тарих. ^0.20
@s3 @date n:1949 жылы | n:29 n:тамызда | мұнда @ussr r:КСРО-ның | алғашқы | атом бомбасы жарылды. ^0.20
@s4 Содан кейін | жарылыстар | @y40 n:қырық n:жыл | тоқтамады. ^0.08 | @k116 n:116-сы — | жер үстінде | және ауада, ^0.04 | @k340 n:340-ы — | жер астында. ^0.12 | Ал @vill жақын ауылдардағы | адамдарды | ешкім @nomove r:көшірмеді. ^0.20
@s5 Түрлі бағалау бойынша, | @mil n:миллионнан n:астам | адам | радиацияның | зардабын тартты. ^0.12 | @sick Ауру көбейді, | балалар | ауру болып туды. ^0.12 | Бірақ бұл туралы | ашық айтуға | @silent r:болмайтын. ^0.24
@s6 Бірақ @y89 n:1989 жылы | ақын @olzhas t:Олжас t:Сүлейменов | @tv теледидардан | халықты | жиналуға шақырды. ^0.08 | Солай @nev t:«Невада t:— t:Семей» | қозғалысы туды. ^0.08 | @sign Жүз мыңдаған адам | қол қойды. ^0.20
@s7 Сөйтіп @closed n:1991 жылы | n:29 n:тамызда | полигон @shut t:жабылды. ^0.08 | Дәл алғашқы | жарылыстан | @d42 n:қырық n:екі n:жыл | өткен күні. ^0.12 | Ал @un БҰҰ | бұл күнді | ядролық сынақтарға қарсы | халықаралық күн | деп жариялады. ^0.24
@s8 t:ҰБТ сұрағы. ^0.08 | Семей полигоны | қай жылы жабылды? ^0.08 | @oA n:1989, | @oB n:1991, | @oC әлде n:1993? ^2.4 | @ans Дұрыс: | g:1991 жылы, | 29 тамызда. ^0.20
@s9 Қазақстан тарихын | терең білгің келсе, | @link профиль @bio шапкасындағы | @go g:сілтемеге өтіңіз.
"""}
# what whisper is expected to hear where the caption text differs from the spoken words
SPOKEN = {'ru': {'1989-й,': 'тысяча девятьсот восемьдесят девятый', '91-й': 'девяносто первый', '93-й?': 'девяносто третий', '1991-м,': '1991', 'ЕНТ,': 'ент', 'ЕНТ.': 'ент'},
          'kk': {'ҰБТ-да': 'өбетеда', 'ҰБТ': 'өбете', '116-сы': '116сы', '340-ы': '340', '29': '29шы', '1989': '1989шы', '1991': '1991шы'}}
norm = lambda s: re.sub(r'[^0-9a-zа-яёәғқңөұүһі]', '', s.lower().replace('ё', 'е'))


def parse(text):
    words, marks, gaps = [], {}, {}
    chunk = 0; pend = []
    for tok in text.replace('\n', ' | ').split():      # a new line (= a new sentence group) also starts a new caption chunk
        if tok == '|': chunk += 1
        elif tok[0] == '@': pend.append(tok[1:])
        elif tok[0] == '^': gaps[len(words) - 1] = float(tok[1:])
        else:
            c = 'w'
            if len(tok) > 2 and tok[1] == ':': c, tok = tok[0], tok[2:]
            glue = tok.endswith('~'); tok = tok.rstrip('~')
            for m in pend: marks[m] = len(words)
            pend = []
            words.append({'w': tok, 'c': c, 'k': chunk, 'glue': glue})
    return words, marks, gaps


def silences(path):
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=noise=-34dB:d=0.12', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)]; e = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]
    return list(zip(s, e))


def align(words, W, lang):
    """Start/end time of every script word from whisper words W = [[t0, t1, text], ...] (char level difflib)."""
    wc, wt = [], []
    for t0, t1, w in W:
        n = norm(w)
        for i, ch in enumerate(n): wc.append(ch); wt.append(t0 + (t1 - t0) * i / max(1, len(n)))
    sc, sw = [], []
    for i, x in enumerate(words):
        for ch in norm(SPOKEN[lang].get(x['w'], x['w'])): sc.append(ch); sw.append(i)
    m = difflib.SequenceMatcher(None, ''.join(sc), ''.join(wc), autojunk=False)
    first = {}
    for a, b, n in m.get_matching_blocks():
        for k in range(n):
            first.setdefault(sw[a + k], []).append((a + k, wt[b + k]))
    t = [None] * len(words)
    for i in range(len(words)):
        if i in first:
            # time of the word's first character: extrapolate back from its first matched char
            pos0 = sw.index(i); a, tm = first[i][0]
            t[i] = tm - (a - pos0) * 0.055
    # fill the gaps by interpolation
    known = [i for i in range(len(words)) if t[i] is not None]
    for i in range(len(words)):
        if t[i] is None:
            p = max([k for k in known if k < i], default=None); n = min([k for k in known if k > i], default=None)
            if p is None: t[i] = max(0, t[n] - .3 * (n - i))
            elif n is None: t[i] = t[p] + .3 * (i - p)
            else: t[i] = t[p] + (t[n] - t[p]) * (i - p) / (n - p)
    for i in range(1, len(t)): t[i] = max(t[i], t[i - 1] + .04)
    return t


def derive(m):
    """Cues computed from the word beats; shared by scene.html (picture) and sfx.py (sound).
    Scene 3 is the film shot (Higgsfield), 1, 2, 4, 5, 7 the map, 6 the 1989 crowd, 8 the ENT quiz, 9 the call to action.
    A film shot starts a little before its sentence and takes the pause in front of it."""
    lead = {2: .12, 3: .4, 4: .45, 5: .12, 6: .5, 7: .3, 8: .4, 9: .12}
    d = {f'S{i}': m[f's{i}'] - lead[i] for i in range(2, 10)}
    return {k: round(v, 3) for k, v in d.items()}


def build(lang):
    words, marks, gaps = parse(SCRIPT[lang])
    W = json.load(open(f'w_{lang}.json'))
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'vo_{lang}_raw.wav', '-f', 's16le', '-ac', '1', '-ar', '48000', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; SR = 48000; dur = len(a) / SR
    t = align(words, W, lang); sil = silences(f'vo_{lang}_raw.wav')
    # snap the word that follows a silence to the end of that silence (whisper tends to start words early)
    for s, e in sil:
        if e - s < .2: continue
        inside = [i for i in range(len(t)) if s - .05 <= t[i] < e]
        if inside: t[inside[0]] = e          # a word cannot start inside a pause
        k = min(range(len(t)), key=lambda i: abs(t[i] - e))
        if abs(t[k] - e) < .28: t[k] = e
    for i in range(1, len(t)): t[i] = max(t[i], t[i - 1] + .04)
    # cuts: middle of the silence that follows the word
    cuts = []
    for i in sorted(gaps):
        nxt = t[i + 1] if i + 1 < len(t) else dur
        cand = [(s, e) for s, e in sil if s > t[i] and s < nxt + .15 and e > t[i] + .05]
        c = (max(cand, key=lambda se: se[1] - se[0]) if cand else (nxt - .08, nxt - .02))
        cuts.append(((c[0] + c[1]) / 2, gaps[i]))
    # remap
    def vt(x): return OFF + x + sum(g for c, g in cuts if x >= c)
    out = np.zeros(int((vt(dur) + TAIL) * SR) + SR, np.float32); prev = 0.0; fade = int(.012 * SR)
    for c, g in cuts + [(dur, 0)]:
        seg = a[int(prev * SR):int(c * SR)].copy()
        if len(seg) > 2 * fade: seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
        i0 = int(vt(prev) * SR) - int(OFF * SR); out[i0:i0 + len(seg)] += seg; prev = c
    last = max(i for i in range(len(a)) if abs(a[i]) > .01) / SR
    end = round(vt(last) + TAIL, 2)
    out = out[:int((end - OFF) * SR)]
    with wave.open(f'vo_{lang}.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    ws = []
    for i, x in enumerate(words):
        t1 = t[i + 1] if i + 1 < len(words) and words[i + 1]['k'] == x['k'] else min(t[i] + .6, (t[i + 1] if i + 1 < len(words) else last))
        ws.append({'w': x['w'], 'c': x['c'], 'k': x['k'], 'g': int(x['glue']), 't': round(vt(t[i]), 3), 'e': round(vt(t1 - 1e-3), 3)})
    B = {'end': end, 'off': OFF, 'words': ws, 'm': {k: ws[i]['t'] for k, i in marks.items()}, 'cuts': [[round(vt(c - 1e-3), 3), g] for c, g in cuts]}
    B['m']['last'] = round(vt(last), 3); B['m'].update(derive(B['m']))
    print(lang, 'raw', round(dur, 2), 'video', end)
    print('  ', ' '.join(f"{x['t']:.2f}|{x['w']}" for x in ws))
    print('  cuts', [(round(c, 2), g) for c, g in cuts])
    print('  marks', B['m'])
    return B


if __name__ == '__main__':
    json.dump({l: build(l) for l in ('ru', 'kk')}, open('beats.json', 'w'), ensure_ascii=False, indent=0)
