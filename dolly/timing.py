"""Timing for the «Dolly the sheep had three mothers» reel.

Aligns the caption script below to the whisper word times of the voice take (w_<lang>.json), inserts a short pause
before every scene, and writes
  vo_<lang>.wav   the voice with the pauses (48 kHz mono); video time = this file + OFF
  beats.json      per language: end, caption chunks with times and colours, named marks (scene starts, card cues)
Markup of SCRIPT:  chunks are separated by |   @name = mark on this chunk   *word = amber word
                   display=spoken when the screen shows something else than the voice says (numbers)
Usage: python3 timing.py
"""
import json, re, subprocess, difflib, os

OFF, TAIL = 0.30, 2.2
PAUSE = {'ru': 0.40, 'kk': 0.30}
WORDS = {'ru': 'w_ru.json', 'kk': 'w_kk.json'}
SCRIPT = {
'ru': """
@s1 У этой овцы | было *три *матери | @oke А *отца | не было вообще
| @s2 Её звали *Долли | Это первый *клон | млекопитающего | из взрослой клетки | @ent И это тема | из биологии *ЕНТ
| @s3 Первая мать — | овца с *белой мордой | @cell Учёные взяли у неё | обычную клетку | вымени | @dna и вынули из неё *ядро | то есть *ДНК
| @s4 Вторая мать — | овца с *чёрной мордой | @egg У неё взяли | *яйцеклетку | @rm и удалили | её собственное ядро | @put Потом в пустую клетку | поместили | ядро первой овцы | @zap и соединили | слабым | *электрическим разрядом
| @s5 Третья мать | выносила | и *родила зародыш | @hard Но всё было | непросто | @try Из *277=277 | попыток | удалась | только *одна
| @s6 *5 *июля *1996 года | родилась *Долли
| @s7 Самое *интересное: | Долли была похожа | не на ту, | что её родила, | @first а только | на *первую овцу | @face Морда *белая | Потому что все *гены | пришли из того ядра | @copy Клон — это | *генетическая *копия
| @s8 Вопрос *ЕНТ | @q Копией какого | организма | является клон? | @o1 Того, кто дал ядро, | кто дал яйцеклетку | или кто родил? | @ans Правильно: | того, кто дал *ядро
| @s9 Чтобы понимать биологию, | а не зубрить, | @cta перейдите по ссылке | в *шапке *профиля
""",
'kk': """
@s1 Бұл қойдың | *үш *анасы болған | @oke Ал *әкесі — | мүлде жоқ
| @s2 Аты — *Долли | Ол — сүтқоректілер | арасында | ересек жасушадан | жасалған | алғашқы *клон | @ent Бұл *ҰБТ | биологиясындағы | тақырып
| @s3 Бірінші ана — | *ақ *тұмсықты қой | @cell Ғалымдар оның | желінінен | кәдімгі бір жасуша | алды да, | @dna ішінен *ядросын, | яғни *ДНҚ-сын | шығарды
| @s4 Екінші ана — | *қара *тұмсықты қой | @egg Одан *жұмыртқа | *жасушасын алып, | @rm оның өз ядросын | алып тастады | @put Сосын бос жасушаға | бірінші қойдың | ядросын салып, | @zap әлсіз | *электр *тогымен | біріктірді
| @s5 Үшінші ана — | ұрықты көтеріп, | *туып берген қой | @hard Бірақ | оңай болмады | @try *277=277 | әрекеттің | тек *біреуі | сәтті шықты
| @s6 *1996 жылы, | *5 *шілдеде | Долли | дүниеге келді
| @s7 Ең *қызығы: | Долли | туған анасына емес, | @first тек *бірінші қойға | ұқсады | @face Тұмсығы *ақ | Өйткені барлық *гендері | сол ядродан келді | @copy Клон деген — | *генетикалық *көшірме
| @s8 *ҰБТ сұрағы | @q Клон қай ағзаның | көшірмесі? | @o1 Ядро берген, | жұмыртқа жасушасын | берген, | әлде туған ана? | @ans Дұрыс: | *ядро берген ағза
| @s9 Биологияны | жаттамай, | түсініп оқу үшін | @cta профиль | *шапкасындағы | сілтемеге өтіңіз
"""}
EXTRA = {'s7': 0.9, 's6': 0.2}   # longer pause around the film shot so the 5 s clip has room
QUIZ = 3.0   # the silence before the answer is stretched to this
norm = lambda s: re.sub(r'[^0-9a-zа-яёәғқңөұүһі]', '', s.lower().replace('ё', 'е'))


def parse(text):
    chunks = []
    for raw in text.replace('\n', ' ').split('|'):
        toks = raw.split(); marks = [t[1:] for t in toks if t[0] == '@']; body = ' '.join(t for t in toks if t[0] != '@')
        if not body: continue
        disp, spoken = (body.split('=') + [None])[:2]
        words = [{'w': w.lstrip('*'), 'c': 'a' if w[0] == '*' else 'w'} for w in disp.split()]
        sp = (spoken or disp.replace('*', '')).split()
        chunks.append({'words': words, 'spoken': sp, 'marks': marks})
    return chunks


def align(spoken, W):
    a = [norm(x) for x in spoken]; b = [norm(w[2]) for w in W]
    T = [None] * len(a)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size): T[blk.a + k] = (W[blk.b + k][0], W[blk.b + k][1])
    # fuzzy: single-word replace spans
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'replace':
            t0, t1 = W[j1][0], W[j2 - 1][1]; n = i2 - i1
            for k in range(n): T[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
    # interpolate the rest
    known = [i for i, x in enumerate(T) if x]
    for i in range(len(T)):
        if T[i] is None:
            p = max([k for k in known if k < i], default=None); q = min([k for k in known if k > i], default=None)
            s = T[p][1] if p is not None else 0; e = T[q][0] if q is not None else s + .3
            T[i] = (s, e)
    return T


def silences(path):
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=noise=-38dB:d=0.06', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return list(zip([float(x) for x in re.findall(r'silence_start: ([\d.]+)', o)], [float(x) for x in re.findall(r'silence_end: ([\d.]+)', o)]))


out = {}
for L in ('ru', 'kk'):
    W = []
    for a, b, w in json.load(open(WORDS[L])):   # whisper glues «Орыс хан» into one word: split it back
        m = re.match(r'^([Оо]рыс)(хан\w*)(.*)$', w)
        if m: h = (a + b) / 2; W += [[a, h, m.group(1)], [h, b, m.group(2) + m.group(3)]]
        else: W.append([a, b, w])
    ch = parse(SCRIPT[L])
    spoken = [w for c in ch for w in c['spoken']]; T = align(spoken, W)
    k = 0
    for c in ch:
        n = len(c['spoken']); c['t0'], c['t1'] = T[k][0], T[k + n - 1][1]; k += n
    take = f'vo_{L}_take.mp3'; S = silences(take)
    # cut points: in the silence just before every scene start (s2..s8)
    cuts, pz = [], []
    P = PAUSE[L]
    for i, c in enumerate(ch):
        sc = any(re.fullmatch(r's[2-9]', m) for m in c['marks'])
        if sc or 'ans' in c['marks']:
            t = c['t0']; best = sorted([s for s in S if s[1] >= t - 1.2 and s[0] <= t + .3], key=lambda s: s[1] - s[0])[-1:] if 'ans' in c['marks'] else [s for s in S if s[1] >= t - .35 and s[0] <= t + .3][-1:]
            if best: cuts.append((best[-1][0] + best[-1][1]) / 2); sil = best[-1][1] - best[-1][0]
            else: cuts.append(t - .05); sil = 0
            ex = sum(EXTRA.get(m, 0) for m in c['marks'])
            pz.append(max(P, QUIZ - sil) if 'ans' in c['marks'] else P + ex)
            if 'ans' in c['marks']: qz = (cuts[-1] - sil / 2, sil)
    shift = lambda t: t + sum(p for x, p in zip(cuts, pz) if x <= t) + OFF
    # voice with pauses
    parts, prev = [], 0.
    for i, x in enumerate(cuts + [None]):
        parts.append(f"[a{i}]atrim={prev}" + (f":{x}" if x else '') + f",asetpts=PTS-STARTPTS[p{i}]")
        if x: parts.append(f"aevalsrc=0:d={pz[i]}:s=48000:c=mono[z{i}]"); prev = x
    seq = ''.join(f'[p{i}]' + (f'[z{i}]' if i < len(cuts) else '') for i in range(len(cuts) + 1))
    nseg = 2 * len(cuts) + 1
    fc = ';'.join(parts) + f';{seq}concat=n={nseg}:v=0:a=1[o]'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', take, '-filter_complex', f"[0:a]aresample=48000,aformat=channel_layouts=mono,asplit={len(cuts)+1}" + ''.join(f'[a{i}]' for i in range(len(cuts)+1)) + ';' + fc, '-map', '[o]', '-ar', '48000', '-ac', '1', f'vo_{L}.wav'], check=True)
    marks, caps = {}, []
    for i, c in enumerate(ch):
        t0, t1 = shift(c['t0']), shift(c['t1'])
        nxt = shift(ch[i + 1]['t0']) if i + 1 < len(ch) else t1 + .6
        caps.append({'t0': round(t0, 3), 't1': round(min(nxt, t1 + .5), 3), 'words': c['words']})
        for m in c['marks']: marks[m] = round(t0, 3)
    # scene starts are put a little before their first word, in the pause
    for m in list(marks):
        if m[0] == 's' and m[1:].isdigit() and m != 's1': marks[m] = round(marks[m] - P * .8, 3)
    marks['s1'] = 0.
    marks['qa'] = round(shift(qz[0]), 3); marks['qb'] = round(marks['qa'] + max(qz[1] + P, QUIZ), 3)
    end = round(shift(ch[-1]['t1']) + TAIL, 3); marks['end'] = end
    out[L] = {'end': end, 'caps': caps, 'm': marks, 'cuts': cuts}
    print(L, 'end', end, {k: v for k, v in marks.items()})
json.dump(out, open('beats.json', 'w'), ensure_ascii=False, indent=0)
