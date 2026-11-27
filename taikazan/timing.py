"""Timing for the «Тайқазан 54 жыл Ленинградта» reel (KZ + RU).

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
@s1 Түркістандағы | екі тонналық қазан | @y54 n:54 жыл | t:Ленинградта тұрды. ^0.2
@s2 Картадан көрсетемін: | @go ол қалай кетті | @back және қалай оралды. | @odd Ал соңында | бір оғаш дерек бар. ^0.3
@s3 Бұл — @maus t:Қожа t:Ахмет t:Ясауи | кесенесі. | Оның орталық залы | @hall t:«Қазандық» деп аталады. | @kaz Ортасында | t:Тайқазан тұрады. ^0.2
@s4 Оны @y1399 n:1399 жылы | @tim t:Әмір t:Темірдің | бұйрығымен құйған. | @master Шебері — | t:Әбдуәзиз t:Тебризи. ^0.2
@s5 Салмағы | @ton шамамен n:екі n:тонна. | @wid Ені n:екі n:жарым | метрге жуық, | @man бойы ұзын адамнан да кең. ^0.2
@s6 Оған шамамен | @l3000 n:3 000 литр | су сыяды. | @bath Бұл — n:20 ваннаға жуық. ^0.3
@s7 @y1935 n:1935-те | Тайқазанды t:Ленинградқа, | @erm t:Эрмитажға алып кетті. | @iran Иран өнерінің | көрмесі үшін. ^0.2
@s8 Жол @km n:3 000 | шақырымнан асты. | @temp Ресми түрде — r:уақытша, | бір көрмеге ғана. ^0.3
@s9 @over Көрме бітті. | @no Бірақ қазан r:қайтпады. | @years Жыл артынан | жыл өтті. ^0.3
@s10 Тек @y1989 n:1989-да, | @after n:54 жылдан кейін, | @home Тайқазан t:Түркістанға оралды. ^0.4
@s11 Ал ең оғашы: | бұл алып қазанда | @meat r:ет асу үшін емес, | @water b:су құю үшін жасалған. | @give Келген жұртқа | одан су таратқан. ^0.3
@s12 @ubt Бұл t:ҰБТ-да келеді. | @q Тайқазан | қай жылы құйылды? | @ans Жауабы: n:1399, | @tim2 Әмір Темірдің бұйрығымен. ^0.3
@s13 Профиль шапкасындағы | @link t:сілтемеге өтіңіз.
""",
 'ru': """
@s1 Двухтонный казан | из t:Туркестана | @y54 n:54 года простоял | в t:Ленинграде. ^0.2
@s2 Покажу на карте, | @go как он уехал | @back и как вернулся. | @odd А в конце | есть одна странная деталь. ^0.3
@s3 Это @maus мавзолей | t:Ходжи t:Ахмеда t:Ясави. | Его центральный зал | @hall называется t:«Казандык». | @kaz В центре стоит t:Тайказан. ^0.2
@s4 Его отлили | @y1399 в n:1399-м | @tim по приказу t:Тимура. | @master Мастер — | t:Абд t:аль-Азиз t:Тебризи. ^0.2
@s5 @ton Весит около n:двух n:тонн. | @wid Почти n:два n:с n:половиной | метра в ширину, | @man шире роста | высокого человека. ^0.2
@s6 В него помещается | @l3000 около n:трёх n:тысяч | литров воды. | @bath Это почти n:20 ванн. ^0.3
@s7 @y1935 В n:1935-м | t:Тайказан увезли | @erm в t:Ленинград, в t:Эрмитаж. | @iran Для выставки | иранского искусства. ^0.2
@s8 @km Больше n:трёх n:тысяч | километров пути. | @temp Официально — r:временно, | только на одну выставку. ^0.3
@s9 @over Выставка закончилась. | @no Но казан r:не r:вернули. | @years Год шёл за годом. ^0.3
@s10 Только @y1989 в n:1989-м, | @after через n:54 года, | @home t:Тайказан вернулся | в t:Туркестан. ^0.4
@s11 А самое странное: | этот гигантский казан | @meat делали r:не r:для r:мяса, | @water а b:для b:воды. | @give Из него раздавали | воду паломникам. ^0.3
@s12 @ubt Это бывает на t:ЕНТ. | @q В каком году | отлит Тайказан? | @ans Ответ: n:1399-й, | @tim2 по приказу Тимура. ^0.3
@s13 Перейдите @link по t:ссылке | в шапке профиля.
""",
}
SPOKEN = {'ru': {}, 'kk': {'ҰБТ-да': 'өбәтедә'}}
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
    """Cues computed from the word beats; shared by scene.html (picture) and sfx.py (sound): S<i> = a little before sentence group i."""
    d = {f'S{i}': m[f's{i}'] - .15 for i in range(2, 14)}
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
