"""Timing for the Isatai POV reel.

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
WORDS = {'ru': 'w_ru.json', 'kk': 'w_kk_med.json'}
SCRIPT = {
'ru': """
@s1 Ты в *1837 году=Ты в тысяча восемьсот тридцать седьмом году | И твоя земля | тебе больше | не *принадлежит
| @s2 Между *Волгой | и *Уралом | @zh Хан *Жангир | и султаны | забрали лучшие | *пастбища | Твоему аулу | негде пасти скот
| @s3 Ночью у костра | ты видишь двоих | Старшина рода Берш | *Исатай *Тайманулы | и поэт | @mah *Махамбет | Стихи Махамбета | будят в тебе | *огонь
| @s4 *Октябрь *1837 года=Октябрь тысяча восемьсот тридцать седьмого года | Ты один из | @cnt *двух *тысяч воинов | @ring Мы окружили | ставку хана
| @s5 Но *15 *ноября=Но пятнадцатого ноября | у *Тастобе | @hit отряд карателей | разбил восставших | @scat Воины разошлись | по своим родам
| @s6 *13 *декабря=Тринадцатого декабря | мы перешли *Урал | @post Царские власти | пообещали | *тысячу *рублей | тому, кто | выдаст Исатая
| @s7 В *июле *1838 года=В июле тысяча восемьсот тридцать восьмого года | у реки *Акбулак | @fade Исатай погиб | @mon А Махамбет | продолжал | свои стихи
| @s8 На *ЕНТ | не путай | две битвы | *Тастобе | и *Акбулак | @cta Чтобы перейти | на следующий *уровень | перейдите по ссылке | в *шапке *профиля
""",
'kk': """
@s1 Сен *1837 жылдасың=Сен мың сегіз жүз отыз жетінші жылдасың | Ал сенің жерің | енді *сенікі *емес
| @s2 *Еділ мен *Жайықтың | арасы | @zh *Жәңгір хан | мен сұлтандар | жақсы *жайылымды | бөліп алды | Сенің ауылыңа | мал бағатын жер | жетпейді
| @s3 Түнде от басында | екі адамды көресің | Беріш руының старшыны | *Исатай *Тайманұлы | және ақын | @mah *Махамбет | Махамбеттің жыры | жүрегіңді *оятады
| @s4 *1837 жылдың *қазаны=Мың сегіз жүз отыз жетінші жылдың қазаны | @cnt Сен *екі *мың | сарбаздың бірісің | @ring Біз хан ордасын | қоршауға алдық
| @s5 Бірақ *15 *қарашада=Бірақ он бесінші қарашада | *Тастөбеде | @hit жазалаушы отрядпен | шайқас болды | @scat Көтерілісшілер | руларына | тарап кетті
| @s6 *13 *желтоқсанда=Он үшінші желтоқсанда | *Жайықтан өттік | @post Патша үкіметі | Исатайды | ұстап бергенге | *мың *сом | сыйақы жариялады
| @s7 *1838 жылы *шілдеде=Мың сегіз жүз отыз сегізінші жылы шілдеде | *Ақбұлақ өзенінің | бойында | @fade Исатай қаза тапты | @mon Махамбет | жырын тоқтатпады
| @s8 *ҰБТ-да | екі шайқасты | шатастырма | *Тастөбе | мен *Ақбұлақ | @cta Келесі *деңгейге | өту үшін | профиль *шапкасындағы | сілтемеге өтіңіз
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
