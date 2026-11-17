"""Timing for the Sulu khagan comic reel.

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
@s1 Арабы так | *боялись | одного | тюркского кагана | что прозвали его | @bod *«Бодливым»
| @s2 *VIII *век=Восьмой век | @map В *Жетысу | *Тюргешский *каганат | @ush Его основал | каган *Ушлик | @suy Ставка стояла | в *Суябе | на реке *Чу
| @s3 В *715 году=В семьсот пятнадцатом году | к власти пришёл | @sulu *Сулу-каган=Сулу каган | Угроза шла | с *трёх сторон | @ar с юго-запада | *арабы | @ch с юго-востока | *Китай | @et с востока | *Восточные *тюрки
| @s4 Сулу сам | шёл в *бой | @clash и раз за разом | *побеждал | @nick За это арабы | прозвали его | *«Абу *Музахим» | то есть | *«Бодливый»
| @s5 Его ставка | была в *Таразе | @horn Ещё одно | его прозвище | *«рогатый *каган»
| @s6 В *738 году=В семьсот тридцать восьмом году | Сулу *погиб | @chn И Китай | сразу пошёл | в *наступление | @tz В *740 году=В семьсот сороковом году | пал *Тараз | @sy в *748-м=в семьсот сорок восьмом | *Суяб | @atl Всё это | привело к битве | при *Атлахе | в *751 году=в семьсот пятьдесят первом году
| @s7 На *ЕНТ | спрашивают | кого арабы | прозвали | *«Бодливым»? | @ans Ответ: | *Сулу-кагана=Сулу кагана | @cta Перейдите | по ссылке | в *шапке *профиля
""",
'kk': """
@s1 Арабтар | бір түрік қағанынан | қатты *қорыққаны | сонша | @bod оған *«Сүзеген» | деп ат қойды
| @s2 *VIII *ғасыр=Сегізінші ғасыр | @map *Жетісуда | *Түргеш *қағанаты | @ush Оның негізін | *Үшлік қаған | қалады | @suy Ордасы | *Шу бойындағы | *Суяб | қаласында болды
| @s3 *715 жылы=Жеті жүз он бесінші жылы | билікке | @sulu *Сұлу қаған келді | Оған *үш жақтан | қауіп төнді | @ar оңтүстік-батыстан=оңтүстік батыстан | *арабтар | @ch оңтүстік-шығыстан=оңтүстік шығыстан | *Қытай | @et шығыстан | *Шығыс *түріктер
| @s4 Сұлу шайқастарға | өзі *қатысты | @clash және үнемі | *жеңіп отырды | @nick Сол үшін | арабтар оны | *«Әбу *Мұзахим» | яғни *«Сүзеген» | деп атады
| @s5 Оның ордасы | *Тараз | қаласында болды | @horn Тағы бір | лақап аты | *«мүйізді *қаған»
| @s6 *738 жылы=Жеті жүз отыз сегізінші жылы | Сұлу *қаза тапты | @chn Сол сәтте | *Қытай | шабуылын | қайта бастады | @tz *740 жылы=Жеті жүз қырқыншы жылы | *Тараз | @sy *748 жылы=жеті жүз қырық сегізінші жылы | *Суяб | басып алынды | @atl Бәрі | *751 жылғы=жеті жүз елу бірінші жылғы | *Атлах | шайқасына әкелді
| @s7 *ҰБТ-да=Ұ-Бе-Те-да | сұрайды | арабтар | *«Сүзеген» деп | кімді атады? | @ans Жауабы: | *Сұлу *қаған | @cta Профиль | *шапкасындағы | сілтемеге | өтіңіз
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
        if any(re.fullmatch(r's[2-9]', m) for m in c['marks']):
            t = c['t0']; best = [s for s in S if s[0] - .25 <= t <= s[1] + .25]
            cuts.append(((best[-1][0] + best[-1][1]) / 2) if best else t - .05)
    P = PAUSE[L]
    shift = lambda t: t + P * sum(1 for x in cuts if x <= t) + OFF
    # voice with pauses
    parts, prev = [], 0.
    for i, x in enumerate(cuts + [None]):
        parts.append(f"[a{i}]atrim={prev}" + (f":{x}" if x else '') + f",asetpts=PTS-STARTPTS[p{i}]")
        if x: parts.append(f"aevalsrc=0:d={P}:s=48000:c=mono[z{i}]"); prev = x
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
