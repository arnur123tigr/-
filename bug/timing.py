"""Timing for the «first bug was a real moth» comic reel.

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
@s1 Почему ошибку | в программе | называют *«баг», | @zhuk то есть *«жук»? | @why Потому что однажды | в компьютере нашли | @real *настоящего *жука
| @s2 Этот термин | встречается и | в *информатике | на *ЕНТ | @funny А история | такая смешная, | что не забудешь
| @s3 *1947 *год,=Тысяча девятьсот сорок седьмой год, | @usa США, *Гарвард | Компьютер тогда — | @room машина размером | с целую *комнату | @relay Внутри тысячи *реле, | маленьких механических | переключателей | @click Они работают | с *щелчками
| @s4 Однажды машина | начала выдавать | *неверный результат | @check Инженеры проверили | программу — | @ok всё *верно | @still Но машина | всё равно *ошибалась
| @s5 Оказалось, | в *семидесятом *реле | @moth застряла *моль!
| @s6 Инженеры приклеили | @tape моль *скотчем | в *журнал | @wrote и написали: | «первый настоящий случай, | когда найден *жук» | @museum Эта страница | сейчас хранится | в *Смитсоновском *музее | в США
| @s7 Интересно, | что словом *«баг» | инженеры называли | поломки и *раньше | @world Но после этой истории | оно разошлось | по всему *миру | @debug А поиск и | исправление ошибок — | @otl *«отладка», | *debugging=по-английски дебаггинг, | @remove буквально | *«убрать *жука»
| @s8 Вопрос *ЕНТ | @q Как называется | поиск и исправление | ошибок в программе? | @o1 Компиляция, | отладка | или архивация? | @ans Правильно: | *отладка!
| @s9 Чтобы учить | информатику | на таких примерах, | @cta перейдите | по ссылке | в *шапке *профиля
""",
'kk': """
@s1 Бағдарламадағы қатені | неге *«баг», | @zhuk яғни *«қоңыз» дейді? | @why Өйткені бір күні | компьютерде | @real *шын *қоңыз табылған
| @s2 Бұл термин | *ҰБТ-ның=Ұ-Бе-Тенің | *информатикасында да | кездеседі | @funny Тарихы | сондай күлкілі, | ұмытпайсың
| @s3 *1947 *жыл,=Мың тоғыз жүз қырық жетінші жыл, | @usa АҚШ, *Гарвард | Сол кездегі компьютер — | @room тұтас *бөлмедей | үлкен машина | @relay Ішінде мыңдаған *реле — | кішкентай механикалық | ажыратқыштар | @click Олар *шырт-шырт етіп | жұмыс істейді
| @s4 Бір күні машина | *қате нәтиже | бере бастады | @check Инженерлер | бағдарламаны тексерді — | @ok бәрі *дұрыс | @still Бірақ машина | бәрібір *жаңылыса берді
| @s5 Сөйтсе, | *жетпісінші *реленің ішінде | @moth *көбелек | қысылып қалған!
| @s6 Инженерлер көбелекті | @tape *скотчпен | *журналға жапсырып, | @wrote «қате тудырған | алғашқы шын қоңыз» | деп жазды | @museum Бұл бет қазір | АҚШ-тағы | *Смитсон *мұражайында | сақтаулы
| @s7 Қызығы, | *«баг» сөзін | инженерлер | бұған *дейін де айтқан | @world Бірақ осы оқиғадан кейін | ол бүкіл *әлемге | тарады | @debug Ал қатені | іздеп түзету — | @otl *«отладка», | *debugging=ағылшынша дебаггинг, | @remove яғни | *«қоңызды *алу»
| @s8 *ҰБТ сұрағы=Ұ-Бе-Те сұрағы | @q Бағдарламадағы қатені | іздеп, түзету | қалай аталады? | @o1 Компиляция, | отладка | әлде архивтеу? | @ans Дұрыс: | *отладка!
| @s9 Информатиканы | осындай қызық | мысалдармен үйрену үшін | @cta профиль | *шапкасындағы | сілтемеге өтіңіз
"""}
EXTRA = {'s6': 0.9}   # the «ой!» beat after the moth shot
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
    W = json.load(open(WORDS[L]))
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
            pz.append(max(P, QUIZ - sil) if 'ans' in c['marks'] else P + sum(EXTRA.get(m, 0) for m in c['marks']))
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
