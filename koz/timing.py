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
from itertools import accumulate as np_cumsum

OFF, TAIL = 0.30, 2.2
PAUSE = {'ru': 0.8, 'kk': 0.7}
QUIZ = 2.6     # extra silence before the quiz answer (3-2-1 timer)
WORDS = {'ru': 'w_ru.json', 'kk': 'w_kk.json'}
SCRIPT = {
'ru': """
@s1 Прямо сейчас | твой *глаз | показывает мир | *вверх *ногами | @hide Но ты этого | не *замечаешь
| @s2 Это частая тема | на *ЕНТ | @min Сейчас разберём *глаз | за одну *минуту
| @s3 У глазного яблока | *три *оболочки | @scl Снаружи | белая *склера | @cor спереди | прозрачная *роговица | @cho В середине | *сосудистая оболочка | @ret Внутри | *сетчатка | @here Изображение появляется | именно *здесь
| @s4 Свет проходит | через *зрачок | @ref и преломляется | в *хрусталике | @lens Хрусталик — | обычная *линза | @inv Поэтому на сетчатке | картинка *уменьшенная | и *перевёрнутая
| @s5 Там | *фоторецепторы | @rod Палочек около | *120 миллионов | они видят | в *темноте | @cone Колбочек | *6–7 миллионов | они различают *цвет | @tease Но самое интересное | *впереди
| @s6 Картинку переворачивает | твой *мозг | @str В *1896 году | учёный *Стрэттон | надел очки | которые *переворачивают мир | @fall Первые дни | он *падал | @ok Через несколько дней | мозг *привык | и всё стало | выглядеть *нормально
| @s7 Проверь *сам | @close Закрой *левый глаз | смотри *правым | на *крестик | @near и приближай *телефон | @gone Точка *исчезнет! | @bs Это *слепое *пятно | там где выходит | *зрительный *нерв | рецепторов *нет
| @s8 Вопрос *ЕНТ | Что различает *цвет? | @opts Палочки, колбочки | или склера? | @ans Правильно: | *колбочки!
| @s9 Хочешь понимать | биологию | вот так просто | @cta перейди по ссылке | в *шапке *профиля
""",
'kk': """
@s1 Дәл қазір | сенің *көзің | әлемді | *төңкеріп көрсетіп тұр | @hide Бірақ сен оны | *байқамайсың
| @s2 Бұл *ҰБТ-да | жиі келетін тақырып | @min Қазір *көзді | бір *минутта ашып көреміз
| @s3 Көз алмасының | *үш *қабығы бар | @scl Сыртқысы — | ақ *склера | @cor алдында мөлдір | *қасаң қабық | @cho Ортаңғысы — | *тамырлы қабық | @ret Ішкісі — | *торлы қабық | @here Сурет дәл | осы жерде | *пайда болады
| @s4 Жарық | *қарашықтан өтіп | @ref көз *бұршағында | сынады | @lens Бұршақ — | кәдімгі *линза | @inv Сондықтан | торлы қабықта кескін | *кішірейген және | *төңкерілген | болып түседі
| @s5 Онда | *фоторецепторлар бар | @rod Таяқшалар — | *120 миллионға жуық | олар *қараңғыда көреді | @cone Сауытшалар — | *6–7 миллион | олар *түсті ажыратады | @tease Бірақ ең қызығы | *алда
| @s6 Суретті | *миың аударып қояды | @str *1896 жылы | ғалым *Стрэттон | әлемді төңкеретін | *көзілдірік киді | @fall Алғашқы күндері | *құлап жүрді | @ok Бірнеше күннен кейін | миы *бейімделіп | бәрі *қалыпты | көріне бастады
| @s7 Қазір өзің *тексер | @close Сол көзіңді *жап | оң көзбен | *крестке қара да | @near *телефонды жақындат | @gone Нүкте *жоғалады! | @bs Бұл — *соқыр *дақ | көру жүйкесі | шығатын жерде | рецептор *жоқ
| @s8 *ҰБТ сұрағы | Түсті не *ажыратады? | @opts Таяқша, сауытша | әлде склера? | @ans Дұрыс: | *сауытша!
| @s9 Биологияны осылай | түсінікті | оқығың келсе | @cta профиль *шапкасындағы | *сілтемеге өтіңіз
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
    # cut points: in the silence just before every scene start (s2..s7)
    cuts, PS = [], []
    for c in ch:
        if any((re.fullmatch(r's[2-9]', m) or m == 'ans') for m in c['marks']):
            t = c['t0']; best = [s for s in S if s[0] - .25 <= t <= s[1] + .25]
            cuts.append(((best[-1][0] + best[-1][1]) / 2) if best else t - .05)
            PS.append(QUIZ if 'ans' in c['marks'] else PAUSE[L])
    P = PAUSE[L]
    cum = [0.] + list(np_cumsum(PS))
    # voice with pauses
    parts, prev = [], 0.
    for i, x in enumerate(cuts + [None]):
        parts.append(f"[a{i}]atrim={prev}" + (f":{x}" if x else '') + f",asetpts=PTS-STARTPTS[p{i}]")
        if x: parts.append(f"aevalsrc=0:d={PS[i]}:s=48000:c=mono[z{i}]"); prev = x
    seq = ''.join(f'[p{i}]' + (f'[z{i}]' if i < len(cuts) else '') for i in range(len(cuts) + 1))
    nseg = 2 * len(cuts) + 1
    fc = ';'.join(parts) + f';{seq}concat=n={nseg}:v=0:a=1[o]'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', take, '-filter_complex', f"[0:a]aresample=48000,aformat=channel_layouts=mono,asplit={len(cuts)+1}" + ''.join(f'[a{i}]' for i in range(len(cuts)+1)) + ';' + fc, '-map', '[o]', '-ar', '48000', '-ac', '1', f'vo_{L}.wav'], check=True)
    marks, caps = {}, []
    ks, k = [], 0
    for c in ch:
        if any((re.fullmatch(r's[2-9]', m) or m == 'ans') for m in c['marks']): k += 1
        ks.append(k)
    sh = lambda t, k: t + cum[k] + OFF          # by scene index: whisper word starts can fall a little before the cut
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
