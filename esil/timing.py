"""Timing for the Esil -> ocean reel (KZ + RU).

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
TAIL = 2.6          # video keeps running after the last word (the end card: logo + call to action)
SCRIPT = {
 'kk': """
@s1 Астанадағы | b:Есілдің суы | қайда барады? | @ocean t:Мұхитқа. ^0.25
@s2 Бірақ ең жақын | t:мұхит | @km n:екі n:мың n:шақырымнан | да алыс. ^0.25
@s3 Тамшы | @three n:үш өзеннен | өтеді. | @odd Ал үшіншісінде | бір r:оғаш r:нәрсе бар. ^0.3
@s4 Бірінші — | @esil b:Есіл. | Ол @pet Петропавлдан өтіп, | @rus Ресейге кетеді. ^0.2
@s5 Сосын | b:Есіл | @conf t:Ертіске құяды. | @long t:Ертіс — | Қазақстандағы | ең ұзын өзен. ^0.25
@s6 t:Ертіс | @cn Қытай тауларынан | басталып, | @zay Зайсан көлі арқылы | @back бізге келеді. ^0.2
@s7 Ертістің ұзындығы — | @len n:4_248 n:шақырым. | @alm Алматыдан Мәскеуге | дейінгі жолдан да | ұзын. ^0.25
@s8 Ал үшінші өзен — | @ob b:Обь. | Оның ұзындығы | @oblen n:3_650 n:шақырым ғана. ^0.3
@s9 @notice Байқадыңыз ба? | @cmp t:Ертіс b:Обьтан ұзын. | @but Бірақ | @sala r:саласы — t:Ертіс. ^0.3
@s10 Сонымен, | Астанадағы су | @arc t:Солтүстік t:Мұзды t:мұхитқа | құяды. | @world Ертіс әлемдегі | ең ұзын | салалардың бірі. ^0.3
@s11 Бұл @ubt t:ҰБТ-да келеді. | @q Қай өзендер | Солтүстік Мұзды мұхит | алабына жатады? | @ans Жауабы: | @a1 t:Ертіс, @a2 t:Есіл, @a3 t:Тобыл. ^0.2
@s12 Профиль шапкасындағы | @link t:сілтемеге өтіңіз.
""",
 'ru': """
@s1 Куда утекает | b:вода b:Есиля | в Астане? | @ocean В t:океан. ^0.25
@s2 Но до ближайшего | t:океана | @km больше n:двух n:тысяч n:километров. ^0.25
@s3 Капля пройдёт | @three n:три реки. | @odd А в третьей | скрыта r:странная r:вещь. ^0.3
@s4 Первая — | @esil b:Есиль. | Он проходит | @pet Петропавловск | @rus и уходит в Россию. ^0.2
@s5 Потом | b:Есиль | @conf впадает t:в t:Иртыш. | @long t:Иртыш — | самая длинная | река Казахстана. ^0.25
@s6 t:Иртыш | начинается | @cn в горах Китая | @zay и через озеро Зайсан | @back приходит к нам. ^0.2
@s7 Длина Иртыша — | @len n:4_248 n:километров. | @alm Длиннее, чем путь | от Алматы до Москвы. ^0.25
@s8 А третья река — | @ob b:Обь. | Её длина всего | @oblen n:3_650 n:километров. ^0.3
@s9 @notice Заметили? | @cmp t:Иртыш длиннее b:Оби. | @but Но притоком | считается | @sala именно t:Иртыш. ^0.3
@s10 Вот так | вода из Астаны | попадает в | @arc t:Северный t:Ледовитый t:океан. | @world А Иртыш — | один из самых | длинных притоков | в мире. ^0.3
@s11 Это бывает @ubt на t:ЕНТ. | @q Какие реки | относятся к бассейну | Северного Ледовитого океана? | @ans Ответ: | @a1 t:Иртыш, @a2 t:Есиль, @a3 t:Тобол. ^0.2
@s12 Перейдите | @link по t:ссылке | в шапке профиля.
""",
}
SPOKEN = {'ru': {'ЕНТ.': 'ент', '4_248': '4248', '3_650': '3650'},
          'kk': {'ҰБТ-да': 'өпе', 'келеді.': 'теді ғеледі', '4_248': '4248', '3_650': '3670'}}
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
    d = {f'S{i}': m[f's{i}'] - .15 for i in range(2, 13)}
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
    json.dump({l: build(l) for l in ('kk', 'ru')}, open('beats.json', 'w'), ensure_ascii=False, indent=0)
