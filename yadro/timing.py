"""Timing for the Bronze Age mines reel.

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
PAUSE = {'ru': 0.9, 'kk': 0.8}
WORDS = {'ru': 'w_ru.json', 'kk': 'w_kk.json'}
SCRIPT = {
'ru': """
@s1 Сколько копать | до *центра *Земли? | @one Но человечество | не прошло | даже *одного *процента | пути
| @s2 Сейчас спустимся *вниз | как на *лифте | @icons Запоминай | каждый слой | он точно будет | на *ЕНТ=на E&T
| @s3 Первый слой | *земная *кора | @ocean Под океаном | она совсем тонкая | *5–10 км=5 -10 километров | @plain Под равниной | *30–40 км=30 -40 | @mount а под горами | *70–80 км=70 -80 | @lay Состоит | из трёх слоёв | @l1 *осадочного | @l2 *гранитного | @l3 и *базальтового
| @s4 Самая глубокая дыра | *Кольская *скважина | @drill Бурили почти | *20 лет | начиная с *1970-го=1970 -го | @res Результат | *12 км=12 километров | @hot На дне было | *180 градусов | и бурение | *остановили
| @s5 Это всего | *0,2%=0 ,2 % | пути до центра | @crust Мы не пробили | даже *кору | @next А что *дальше?
| @s6 Дальше *мантия | @m29 Она тянется | до глубины | *2900 км=2900 километров | @hot2 Чем глубже | тем *горячее | @ast Мягкий слой | в её верхней части | *астеносфера | @plates По нему и движутся | *плиты
| @s7 В самом центре | *ядро | @core Оно лежит | от *2900=от 2900 | до *6371 км=до 6371 километра | @kgrad Там тысячи | *градусов | Туда не доберётся | ни один *бур
| @s8 Вопрос *ЕНТ=Вопрос E&T | @q До какой глубины | тянется *мантия? | @opts 400, 2900=400, 2900 | или 6371 км?=или 6371 километр | @wait Правильно | *2900 км=2900 километров
| @s9 Чтобы учить географию | *интересно и *легко | @cta Перейдите по ссылке | в *шапке *профиля
""",
'kk': """
@s1 Жердің ортасына | дейін қазсаң | қанша *жүресің? | @one Бірақ адамзат | әлі *бір *пайызына да | жеткен жоқ
| @s2 Қазір *лифтпен | төмен түсеміз | @icons Әр қабатты | есте сақта | ол *ҰБТ-да | міндетті түрде келеді
| @s3 Бірінші | *жер *қыртысы | @ocean Мұхит астында | ол жұп-жұқа | *5–10 км=510 шақырым | @plain Жазықта | *30–40 км=30-40 | @mount ал тау астында | *70–80 км=780 шақырым | @lay Үш қабаттан | тұрады | @l1 *шөгінді | @l2 *гранитті | @l3 *базальтты
| @s4 Ең терең қазба | *Кола *ұңғымасы | @drill *1970 жылдан=1970 жылдан | бастап | *20 жылға жуық=20 жылға жоқ | бұрғылады | @res Нәтиже | *12 км=12 шақырым | @hot Түбінде | *180 градус | ыстық болды да | бұрғылау *тоқтады
| @s5 Бұл центрге дейінгі | жолдың небәрі | *0,2%=нөл бітін ұнған екі пайызы | @crust Тіпті жер қыртысын да | толық *тесе *алмадық | @next Ал әрі қарай | не *бар?
| @s6 Одан кейін | *мантия | @m29 Ол *2900 км=2900 шақырым | тереңдікке дейін созылады | @hot2 Тереңдеген сайын | *температура өседі | @ast Жоғарғы бөлігіндегі | жұмсақ қабат | *астеносфера | @plates Тақталар | соның үстінде | *жылжиды
| @s7 Ең ортасында | *ядро | @core Ол *2900-ден=2900-ден | *6371 км=6371 шақырымға | дейін | @kgrad Мұнда температура | *мыңдаған градус | Ол жаққа | ешбір *бұрғы | жетпейді
| @s8 *ҰБТ *сұрағы | @q Мантия | қай тереңдікке | дейін *созылады? | @opts 400, 2900=400, 2900 | әлде 6371 км?=Әлде 6371 шақырым | @wait Дұрыс | *2900 км=2900 шақырым
| @s9 Географияны | *қызықты әрі *оңай | оқу үшін | @cta Профиль шапкасындағы | *сілтемеге өтіңіз
"""}
WAIT = 3.0
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
    # cut points: in the silence just before every scene start (s2..s7)
    cuts, pz = [], []
    for c in ch:
        if any(re.fullmatch(r's[2-9]', m) or m == 'wait' for m in c['marks']):
            t = c['t0']; best = [s for s in S if s[0] - .25 <= t <= s[1] + .25]
            cuts.append(((best[-1][0] + best[-1][1]) / 2) if best else t - .05)
            pz.append(WAIT if 'wait' in c['marks'] else PAUSE[L])
    P = PAUSE[L]
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
    ks, k = [], 0
    for c in ch:
        if any(re.fullmatch(r's[2-9]', m) or m == 'wait' for m in c['marks']): k += 1
        ks.append(k)
    sh = lambda t, k: t + sum(pz[:k]) + OFF          # by scene index: whisper word starts can fall a little before the cut
    for i, c in enumerate(ch):
        t0, t1 = sh(max(c['t0'], cuts[ks[i] - 1]) if ks[i] else c['t0'], ks[i]), sh(c['t1'], ks[i])
        nxt = sh(ch[i + 1]['t0'], ks[i + 1]) if i + 1 < len(ch) else t1 + .6
        caps.append({'t0': round(t0, 3), 't1': round(min(nxt, t1 + .5), 3), 'words': c['words']})
        for m in c['marks']: marks[m] = round(t0, 3)
    # scene starts are put a little before their first word, in the pause
    for m in list(marks):
        if m[0] == 's' and m[1:].isdigit() and m != 's1': marks[m] = round(marks[m] - P * .8, 3)
    marks['s1'] = 0.
    end = round(sh(ch[-1]['t1'], ks[-1]) + TAIL, 3); marks['end'] = end
    out[L] = {'end': end, 'caps': caps, 'm': marks, 'cuts': cuts}
    print(L, 'end', end, {k: v for k, v in marks.items()})
json.dump(out, open('beats.json', 'w'), ensure_ascii=False, indent=0)
