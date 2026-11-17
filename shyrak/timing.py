"""Timing for the Shyrak reel.

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
@s1 Один старый | t:пастух победил | войско целого | r:царя. ^0.20 | @nosw Без t:меча. ^0.75
@s2 @y519 n:519 n:год | до нашей эры. ^0.35 | Персидский царь | @darius r:Дарий r:I | пошёл войной | на @saka t:саков-тиграхауда, | @caps «носящих остроконечные | шапки». ^0.60
@s3 По легенде, | тогда пастух | по имени @shyrak t:Шырак | @wound изранил себя | и пришёл | к r:персам. ^0.55
@s4 Он говорит: | «Саки замучили меня, | я @road покажу | вам дорогу». ^0.35 | И @days n:семь n:дней | ведёт войско | в @desert безводную t:пустыню. ^0.60
@s5 На @day7 n:седьмой n:день | персы увидели | перед собой | только t:песок | и t:солнце. ^0.80
@s6 А что говорят | исторические источники? ^0.35 | По @behistun t:Бехистунской | надписи | @darius2 r:Дарий взял | в плен | сакского вождя | @skunkha t:Скунху, ^0.30 | но в @memory памяти | народа остался | @feat подвиг t:Шырака. ^0.80
@s7 Он отдал t:жизнь, | чтобы защитить | свою t:землю. ^0.90
@s8 Запомни для ЕНТ: ^0.25 | @e1 n:519 год | до нашей эры, | @e2 r:Дарий r:I, | @e3 t:саки-тиграхауда. ^0.55
@s9 Изучай такую | историю вместе с нами. ^0.25 | @link Перейдите | по @go g:ссылке | в @bio шапке профиля.
""",
 'kk': """
@s1 Бір қарт | t:бақташы | бүкіл бір | патшаның r:әскерін | жеңді. ^0.20 | @nosw t:Қылышсыз. ^0.70
@s2 Біздің заманымызға | дейінгі @y519 n:519 n:жыл. ^0.35 | Парсы патшасы | @darius r:І r:Дарий | шошақ бөрікті | @saka t:сақтарға, | t:сақ-тиграхаудаларға | жорыққа шықты. ^0.55
@s3 Аңыз бойынша, | сол кезде | @shyrak t:Шырақ деген | бақташы | @wound өз денесін жаралап, | r:парсыларға барады. ^0.50
@s4 Ол: «Сақтар | мені азаптады, | мен @road сендерге | жол көрсетемін» | дейді. ^0.30 | Сөйтіп әскерді | @days n:жеті n:күн бойы | @desert сусыз t:шөлге | алып кетеді. ^0.55
@s5 @day7 n:Жетінші n:күні | парсылар алдында | тек t:құм мен | t:күнді көрді. ^0.70
@s6 Ал тарихи деректер | не дейді? ^0.30 | @behistun t:Бехистун жазуы | бойынша | @darius2 r:Дарий сақ көсемі | @skunkha t:Скунханы | тұтқынға алған. ^0.30 | Бірақ @memory халық есінде | @feat t:Шырақтың ерлігі | қалды. ^0.80
@s7 Ол t:жерін | қорғау үшін | өз t:өмірін берді. ^0.90
@s8 ҰБТ-ға есте сақта: ^0.25 | @e1 Біздің заманымызға | дейінгі n:519 жыл, | @e2 r:І r:Дарий, | @e3 t:сақ-тиграхаудалар. ^0.55
@s9 Мұндай тарихты | бізбен бірге оқы. ^0.25 | @link Профиль @bio шапкасындағы | @go g:сілтемеге өтіңіз.
"""}
# what whisper is expected to hear where the caption text differs from the spoken words
SPOKEN = {'ЕНТ:': 'ент', 'ҰБТ-ға': 'өбөтіға', 'І': 'бірінші'}
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


def align(words, W):
    """Start/end time of every script word from whisper words W = [[t0, t1, text], ...] (char level difflib)."""
    wc, wt = [], []
    for t0, t1, w in W:
        n = norm(w)
        for i, ch in enumerate(n): wc.append(ch); wt.append(t0 + (t1 - t0) * i / max(1, len(n)))
    sc, sw = [], []
    for i, x in enumerate(words):
        for ch in norm(SPOKEN.get(x['w'], x['w'])): sc.append(ch); sw.append(i)
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
    Scenes 1, 3, 5, 7 are the film shots (Higgsfield), 2, 4, 6, 8, 9 the map. A film shot starts a little before its sentence
    and takes the pause in front of it, so that the picture breathes before the voice comes in."""
    lead = {2: .12, 3: .38, 4: .12, 5: .45, 6: .12, 7: .7, 8: .14, 9: .12}
    d = {f'S{i}': m[f's{i}'] - lead[i] for i in range(2, 10)}
    return {k: round(v, 3) for k, v in d.items()}


def build(lang):
    words, marks, gaps = parse(SCRIPT[lang])
    W = json.load(open(f'w_{lang}.json'))
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'vo_{lang}_raw.wav', '-f', 's16le', '-ac', '1', '-ar', '48000', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; SR = 48000; dur = len(a) / SR
    t = align(words, W); sil = silences(f'vo_{lang}_raw.wav')
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
