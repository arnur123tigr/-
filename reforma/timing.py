"""Timing for the reel: sentences of the voiceover (start/end seconds in the take, from whisper and silence detection),
captions with colour marks, named beats. Writes beats.json (video time = take time + OFF), read by scene.html, sfx.py, mix.py.
Markup:  |  caption chunk     a: amber word   r: red word     @name  beat on the next word
Word times inside a sentence are spread by spoken length (numbers count as long words); EXACT pins measured word starts.
Usage: python3 timing.py"""
import json, re

OFF = 0.30          # the voice starts this late in the video
TAIL = 2.2          # the end card after the last word
S = {
'ru': [
 (0.00, 4.38, "@s1 Подписали a:две a:бумаги, | и казахскую степь | @cut разрезали на | a:шесть a:областей."),
 (4.88, 7.54, "@s2 Всё началось | в @y1822 a:1822 году."),
 (8.02, 11.14, "@sper Устав a:Сперанского | упразднил r:ханскую r:власть | в @orta Среднем жузе."),
 (11.49, 13.66, "Через @y1824 два года | хана не стало | и в @kishi Младшем."),
 (14.03, 19.00, "@s3 В a:1867 году | @alex император | a:Александр a:II | подписал первое положение."),
 (19.39, 22.34, "На юге появились | @zhet a:Семиреченская | и @syr a:Сырдарьинская | области."),
 (22.74, 25.60, "@s4 В a:1868 году | ещё a:четыре:"),
 (25.86, 29.08, "@ural a:Уральская, | @turg a:Тургайская, | @akm a:Акмолинская | и @sem a:Семипалатинская."),
 (29.48, 32.16, "@gg Вся степь подчинилась | a:трём | a:генерал-губернаторствам."),
 (32.49, 35.20, "@buk a:Букеевскую a:Орду | отдали | @astr Астраханской губернии."),
 (35.44, 37.14, "@s5 Власть разбили | на a:пять a:ступеней."),
 (37.43, 39.58, "@top Наверху сидели | только r:русские r:чиновники."),
 (39.93, 42.12, "@low Казахам оставили | лишь a:волость и a:аул."),
 (42.48, 45.72, "@s6 На каждый очаг | ввели @tax a:кибиточный a:налог: | @three три рубля | с юрты."),
 (45.99, 49.16, "@sult А султанов | освободили от налога | и назначили им a:пенсию."),
 (49.55, 51.16, "@s7 Запомни для ЕНТ:"),
 (52.34, 57.14, "@d a:1867–1868 годы, | @g3 a:три генерал-губернаторства, | @o6 a:шесть областей."),
 (57.44, 59.14, "@s8 Готовь такие темы | вместе с нами."),
 (59.50, 61.24, "@link Перейдите по ссылке | в шапке профиля."),
],
'kk': [
 (0.00, 5.14, "@s1 a:Екі a:қағазға | қол қойылды, | сөйтіп қазақ даласы | @cut a:алты a:облысқа | бөлінді."),
 (5.71, 8.46, "@s2 Бәрі @y1822 a:1822 жылы | басталды."),
 (9.02, 11.96, "@sper a:Сперанский жарғысы | @orta Орта жүзде | r:хан r:билігін жойды."),
 (12.53, 15.14, "@y1824 Екі жылдан кейін | @kishi Кіші жүзде де | хан қалмады."),
 (15.87, 20.64, "@s3 a:1867 жылы | @alex патша a:ІІ a:Александр | бірінші ережеге | қол қойды."),
 (21.22, 23.66, "Оңтүстікте | @zhet a:Жетісу мен | @syr a:Сырдария облыстары | пайда болды."),
 (24.98, 27.74, "@s4 a:1868 жылы | тағы a:төрт облыс:"),
 (28.11, 30.68, "@ural a:Орал, @turg a:Торғай, | @akm a:Ақмола, @sem a:Семей."),
 (31.27, 33.92, "@gg Бүкіл дала | a:үш генерал-губернаторлыққа | бағынды."),
 (34.46, 37.12, "@buk a:Бөкей a:Ордасы | @astr Астрахан губерниясына | қосылды."),
 (37.69, 39.22, "@s5 Билік a:бес a:сатыға | бөлінді."),
 (39.76, 42.44, "@top Жоғарғы үшеуінде | тек r:орыс r:шенеуніктері | отырды."),
 (42.91, 45.62, "@low Қазаққа тек | a:болыс пен a:ауыл | старшыны қалды."),
 (46.15, 49.56, "@s6 Әр шаңыраққа | @tax a:түтін a:салығы салынды: | @three үй басына | үш сом."),
 (50.08, 53.10, "@sult Ал сұлтандар | салықтан босатылып, | a:зейнетақы алды."),
 (53.92, 55.24, "@s7 ҰБТ-ға есте сақта:"),
 (55.75, 61.18, "@d a:1867–1868 жылдар, | @g3 a:үш генерал-губернаторлық, | @o6 a:алты облыс."),
 (61.68, 63.68, "@s8 Мұндай тақырыптарды | бізбен бірге дайында."),
 (64.05, 65.94, "@link Профиль шапкасындағы | сілтемеге өтіңіз."),
]}
EXACT = {'ru': {'zhet': 20.16, 'syr': 21.16, 'ural': 25.78, 'turg': 26.58, 'akm': 27.36, 'sem': 28.22, 'three': 44.74, 'd': 52.34, 'g3': 54.70, 'o6': 56.34},
         'kk': {'ural': 28.11, 'turg': 28.81, 'akm': 29.54, 'sem': 30.30, 'd': 55.75, 'g3': 58.67, 'o6': 60.33}}


def weight(w):
    if re.fullmatch(r'\d{4}–\d{4}', w): return 46
    if re.fullmatch(r'\d{4}', w): return 27
    if w in ('II', 'ІІ'): return 7
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
    sent = [[round(a + OFF, 3), round(b + OFF, 3)] for a, b, _ in sents]
    last = sent[-1][1]
    cues = {'S2': marks['s2'] - .25, 'S3': marks['s3'] - .25, 'S4': marks['s4'] - .2, 'S5': marks['s5'] - .25, 'S6': marks['s6'] - .25,
            'S7': marks['s7'] - .2, 'S8': marks['s8'] - .2, 'End': last + .25}
    marks.update({k: round(v, 3) for k, v in cues.items()})
    out[lang] = {'end': round(last + TAIL, 2), 'off': OFF, 'm': marks, 'words': words, 'sent': sent}
    print(lang, 'end', out[lang]['end'], {k: marks[k] for k in ('S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'End')})
json.dump(out, open('beats.json', 'w'), ensure_ascii=False, indent=0)
