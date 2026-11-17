"""Timing for the reel: voice sentences (start/end in the take, from whisper word times), caption chunks with colour
marks, named beats. Writes beats.json (video time = take time + OFF), read by scene.html, sfx.py, mix.py.
Markup:  |  caption chunk     a: amber word   r: red word     @name  beat on the next word
Word times inside a sentence are spread by spoken length (numbers count as long words); EXACT pins measured word starts.
Usage: python3 timing.py"""
import json, re

OFF = 0.30          # the voice starts this late in the video
TAIL = 2.4          # the end card after the last word
S = {
'ru': [
 (0.00, 1.80, "@s1 a:17 a:миллионов | a:десятин."),
 (2.20, 4.30, "Столько земли | r:отняли у казахов."),
 (4.60, 7.84, "@s2 Это около | @km a:185 a:тысяч | квадратных километров,"),
 (8.16, 10.06, "@kg почти вся | территория a:Кыргызстана."),
 (10.50, 14.42, "@s3 В @y1861 a:1861 году | в России | отменили | крепостное право."),
 (14.70, 16.88, "@flow Безземельные крестьяне | хлынули на восток."),
 (17.20, 22.36, "@y1868 С a:1868 года | в Семиречье | каждому переселенцу | @d30 давали по a:тридцать | a:десятин."),
 (22.70, 25.84, "@s4 В a:1892 году | начали строить | @ts a:Транссиб."),
 (26.10, 30.00, "@st На станциях | @petro Петропавловска | @omsk и Омска | скопились | десятки тысяч | переселенцев."),
 (30.30, 33.76, "@s5 В a:1906 году | началась | аграрная реформа | a:Столыпина."),
 (34.10, 40.56, "@yr С a:1871 по a:1917 год | в Казахстан | @mil переселилось больше | a:полутора a:миллионов | крестьян."),
 (40.80, 43.10, "@s6 Земли | становилось r:меньше, | а налог r:рос."),
 (43.50, 47.48, "Кибиточный налог | вырос @c1 с a:полутора | рублей | @c2 до a:трёх, | @c3 а потом до a:четырёх."),
 (47.70, 54.60, "@s7 В a:1913 году | Ахмет Байтурсынулы | написал, | что под вопросом | оказалось само | существование | казахского народа."),
 (54.90, 57.14, "@s8 Запомни | эти a:три a:числа | для ЕНТ."),
 (57.40, 59.18, "@link Перейдите по ссылке | в шапке профиля."),
],
'kk': [
 (0.00, 1.52, "@s1 a:17 a:миллион | a:десятина."),
 (1.98, 3.82, "Бұл қазақтан | r:тартып r:алынған жер."),
 (4.38, 7.22, "@s2 Бұл шамамен | @km a:185 a:мың | шаршы шақырым."),
 (7.76, 9.52, "@kg Бүкіл a:Қырғызстанның | жеріндей дерлік."),
 (10.46, 14.44, "@s3 @y1861 a:1861 жылы | Ресейде | басыбайлы құқық | жойылды."),
 (15.02, 17.12, "@flow Жерсіз шаруалар | шығысқа ағылды."),
 (17.78, 23.98, "@y1868 a:1868 жылы | Жетісуда | әр қоныс аударушыға | @d30 a:отыз a:десятинадан | жер берілді."),
 (24.30, 28.78, "@s4 a:1892 жылы | @ts a:Транссібір | теміржолы | салына бастады."),
 (29.30, 33.42, "@st @petro Петропавл | @omsk мен Омбы | бекеттерінде | ондаған мың | қоныс аударушы | жиналды."),
 (34.06, 38.24, "@s5 a:1906 жылы | a:Столыпиннің | аграрлық реформасы | басталды."),
 (38.78, 46.30, "@yr a:1871 жылдан | a:1917 жылға дейін | Қазақстанға | @mil a:бір a:жарым a:миллионнан | астам шаруа | көшіп келді."),
 (46.82, 49.16, "@s6 Жер r:азайды, | ал салық r:өсті."),
 (49.25, 54.20, "Түтін салығы | @c1 a:бір a:жарым сомнан | @c2 a:үшке, | @c3 кейін a:төрт сомға | дейін көтерілді."),
 (54.74, 61.80, "@s7 a:1913 жылы | Ахмет Байтұрсынұлы | қазақ ұлтының | өмір сүруінің өзі | проблемаға айналды | деп жазды."),
 (62.70, 65.80, "@s8 Бұл a:үш санды | ҰБТ-ға | есте сақта."),
 (66.30, 68.44, "@link Профиль шапкасындағы | сілтемеге өтіңіз."),
]}
EXACT = {'ru': {'km': 5.0, 'd30': 21.3, 'ts': 25.34, 'petro': 26.7, 'omsk': 27.4, 'mil': 38.6, 'c1': 44.8, 'c2': 45.8, 'c3': 47.0},
         'kk': {'km': 5.1, 'd30': 21.9, 'ts': 26.5, 'petro': 29.3, 'omsk': 29.9, 'mil': 43.8, 'c1': 50.5, 'c2': 51.5, 'c3': 52.7}}


def weight(w):
    if re.fullmatch(r'\d{4}', w): return 27
    if re.fullmatch(r'\d+', w): return 4 + 5 * len(w)
    return len(re.sub(r'[^\wәғқңөұүһі-]', '', w.lower())) + 1.5


out = {}
for lang, sents in S.items():
    words, marks, chunk = [], {}, 0
    for si, (a, b, text) in enumerate(sents):
        toks, pend = [], []
        for tok in text.split():
            if tok == '|': chunk += 1; continue
            if tok[0] == '@': pend.append(tok[1:]); continue
            c = 'w'
            if len(tok) > 2 and tok[1] == ':': c, tok = tok[0], tok[2:]
            toks.append({'w': tok, 'c': c, 'k': chunk, 's': si, 'm': pend}); pend = []
        chunk += 1
        ws = [weight(t['w']) for t in toks]; tot = sum(ws); acc = 0
        for t, wt in zip(toks, ws):
            t['t0'] = round(a + (b - a) * acc / tot + OFF, 3); acc += wt; t['t1'] = round(a + (b - a) * acc / tot + OFF, 3)
            for m in t.pop('m'): marks[m] = t['t0']
        words += toks
    for k, v in EXACT[lang].items(): marks[k] = round(v + OFF, 3)
    last = sents[-1][1] + OFF
    cues = {'S2': marks['s2'] - .3, 'S3': marks['s3'] - .3, 'S4': marks['s4'] - .3, 'S5': marks['s5'] - .3, 'S6': marks['s6'] - .3,
            'S7': marks['s7'] - .35, 'S8': marks['s8'] - .3, 'End': marks['link'] - .15}
    marks.update({k: round(v, 3) for k, v in cues.items()})
    out[lang] = {'end': round(last + TAIL, 2), 'off': OFF, 'm': marks, 'words': words, 'sent': [[a + OFF, b + OFF] for a, b, _ in sents]}
    print(lang, 'end', out[lang]['end'], {k: marks[k] for k in ('S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'End')})
json.dump(out, open('beats.json', 'w'), ensure_ascii=False, indent=0)
