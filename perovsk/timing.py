"""Timing for the «Perovsk» city-names reel.

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
PAUSE = {'ru': 0.30, 'kk': 0.30}
QUIZ = 2.2   # extra silence before the quiz answer (the take already has ~1 s): the viewer gets ~3 s to think
WORDS = {'ru': 'w_ru.json', 'kk': 'w_kk.json'}
SCRIPT = {
'ru': """
@s1 Один город | назвали в честь | *генерала | который взял его | *штурмом | @kz Это *Кызылорда
| @s2 Покажу | на одной линии | @ak Сначала | это был *Ақмешіт=Сначала это был Акмешит | кокандская крепость | на *Сырдарье | @mq Название | от «белой *мечети»
| @s3 В *1853 году | с войском пришёл | @ph оренбургский | генерал-губернатор | *Перовский | @sg Он осадил крепость | и взял её *штурмом
| @s4 После этого | крепость назвали | @n2 *«Форт *Перовский» | @n3 С *1867 года | *Перовск | @n4 То есть город | носил имя того | кто его *захватил
| @s5 Народ | с этим *не *смирился | @rd В *1856 году | батыр *Жанкожа | напал на форт Перовск | @age Ему тогда | было *за *80
| @s6 Имя генерала | убрали только | в *1922 году | @n5 город снова | стал *Ақмешіт=стал Акмешит | @n6 А с *1925 года | *Кызылорда
| @s7 Вопрос | с *ЕНТ | Кто взял Ақмешіт=Кто взял Акмешит | в *1853 году | @op Колпаковский | Черняев | или Перовский | @ans Правильно | *Перовский
| @s8 А как раньше | назывался | *твой город | Такие вопросы | часто бывают | на *ЕНТ | @cta Перейдите | по ссылке | в *шапке *профиля
""",
'kk': """
@s1 Бір қаланы | оны *шабуылмен | алған | *генералдың | атымен атады | @kz Ол — *Қызылорда
| @s2 Бір сызықта | көрсетемін | @ak Басында | бұл *Ақмешіт еді | Сырдария бойындағы | *Қоқан бекінісі | @mq Аты | «ақ *мешіттен» | шыққан
| @s3 *1853 жылы=Мың сегіз жүз елу үшінші жылы | @ph Орынбор | генерал-губернаторы | *Перовский | әскерімен келді | @sg Бекіністі қоршап | *шабуылмен алды
| @s4 Содан бекіністі | @n2 *«Форт *Перовский» | деп атады | @n3 *1867 жылдан=Мың сегіз жүз алпыс жетінші жылдан | *Перовск | @n4 Яғни қала | өзін жаулаған | адамның атын | алып жүрді
| @s5 Халық бұған | *көнбеді | @rd *1856 жылы=Мың сегіз жүз елу алтыншы жылы | *Жанқожа батыр | Перовск бекінісіне | шабуыл жасады | @age Ол кезде | оның жасы | *сексеннен асқан еді
| @s6 Генералдың аты | *1922 жылы=мың тоғыз жүз жиырма екінші жылы | ғана алынды | @n5 қала қайта | *Ақмешіт болды | @n6 Ал *1925 жылдан=Ал мың тоғыз жүз жиырма бесінші жылдан | бастап | *Қызылорда
| @s7 *ҰБТ сұрағы=Ұ Бе Те сұрағы | *1853 жылы=Мың сегіз жүз елу үшінші жылы | Ақмешітті | кім алды | @op Колпаковский | Черняев | әлде Перовский | @ans Дұрыс жауап | *Перовский
| @s8 Сенің қалаңның | бұрынғы аты | *қандай еді | Мұндай сұрақтар | *ҰБТ-да=Ұ Бе Те де | жиі келеді | @cta Профиль | *шапкасындағы | сілтемеге өтіңіз
"""}
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
    W = json.load(open(WORDS[L])); ch = parse(SCRIPT[L])
    spoken = [w for c in ch for w in c['spoken']]; T = align(spoken, W)
    k = 0
    for c in ch:
        n = len(c['spoken']); c['t0'], c['t1'] = T[k][0], T[k + n - 1][1]; k += n
    take = f'vo_{L}_take.mp3'; S = silences(take)
    # cut points: in the silence just before every scene start (s2..s8)
    cuts = []
    for c in ch:
        sc = any(re.fullmatch(r's[2-9]', m) for m in c['marks'])
        if sc or 'ans' in c['marks']:
            t = c['t0']; best = [s for s in S if s[0] - .25 <= t <= s[1] + .25]
            cuts.append((((best[-1][0] + best[-1][1]) / 2) if best else t - .05, PAUSE[L] if sc else QUIZ))
            c['t0'] = max(c['t0'], best[-1][1] - .05 if best else t)   # whisper sometimes glues the silence to the next word
    P = PAUSE[L]
    shift = lambda t: t + sum(p for x, p in cuts if x <= t) + OFF
    # voice with pauses
    parts, prev = [], 0.
    for i, xp in enumerate(cuts + [None]):
        x = xp[0] if xp else None
        parts.append(f"[a{i}]atrim={prev}" + (f":{x}" if x else '') + f",asetpts=PTS-STARTPTS[p{i}]")
        if x: parts.append(f"aevalsrc=0:d={xp[1]}:s=48000:c=mono[z{i}]"); prev = x
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
    end = round(shift(ch[-1]['t1']) + TAIL, 3); marks['end'] = end
    out[L] = {'end': end, 'caps': caps, 'm': marks, 'cuts': cuts}
    print(L, 'end', end, {k: v for k, v in marks.items()})
json.dump(out, open('beats.json', 'w'), ensure_ascii=False, indent=0)
