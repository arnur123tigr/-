"""Timing for the USSR reel (KZ + RU).

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
@s1 t:Қазақстан | Кеңес Одағынан | ең @last1 n:соңғы болып шықты. | @why Неге? ^0.2
@s2 Картадан көрсетемін: | @n15 n:он n:бес республика | бір-бірлеп | қалай кетті. | @dot Ал соңғы нүкте | қайда қойылғаны | таң қалдырады. ^0.2
@s3 Кеңес Одағы | жер құрлығының | @sixth n:алтыдан n:бірін | алып жатты. ^0.2
@s4 Бірінші болып | @lt t:Литва шықты. | Мың тоғыз жүз | тоқсанның @lt2 наурызында. ^0.2
@s5 Мың тоғыз жүз | тоқсан бірдің | тамызында | @msk t:Мәскеуде | @putsch r:бүлік болды. | @chain Сосын | тізбек басталды. ^0.2
@s6 @ee t:Эстония, | @lv t:Латвия, | @ua t:Украина, | @by t:Беларусь, | @md t:Молдова. | Бір апта ішінде | бірінен соң бірі. ^0.2
@s7 Күзде | @kg t:Қырғызстан, | @uz t:Өзбекстан, | @tj t:Тәжікстан, | @tm t:Түрікменстан да кетті. | @cau t:Кавказ да кетті. ^0.2
@s8 Ал t:Қазақстан | @wait күтті. | Наурыздағы | @ref референдумда | халықтың | @p94 n:тоқсан n:төрт n:пайызы | одақты сақтауға | дауыс берген еді. ^0.2
@s9 Бірақ | @d8 n:сегізінші n:желтоқсанда | @three Ресей, Украина | және Беларусь | басшылары | @bel t:Беловежде | Кеңес Одағының | @gone r:жойылғанын | жариялады. ^0.3
@s10 @d16 n:Он n:алтыншы n:желтоқсанда | t:Қазақстан | @ind t:тәуелсіздігін | жариялады. | @zh Желтоқсан оқиғасынан | кейін | дәл @five n:бес n:жыл | өткен күні. ^0.3
@s11 Ал Одақтың | соңғы нүктесі | @msk2 Мәскеуде емес, | @alm t:Алматыда | қойылды. | @d21 n:Жиырма n:бірінші n:желтоқсанда | @n11 n:он n:бір ел | осында | @cis t:ТМД-ны құрды. | @gorb Төрт күннен кейін | Горбачев @gk кетті. ^0.3
@s12 Бұл @ubt t:ҰБТ-да келеді. | @q Қазақстан | тәуелсіздігі | қай күні | жарияланды? | @ans Жауабы: | мың тоғыз жүз | тоқсан бірдің | n:он n:алтыншы n:желтоқсаны. ^0.2
@s13 Профиль шапкасындағы | @link t:сілтемеге өтіңіз.
""",
 'ru': """
@s1 t:Казахстан | вышел из | Советского Союза | @last1 t:последним. | @why Почему? ^0.2
@s2 Покажу на карте, | как @n15 n:пятнадцать республик | уходили | одна за другой. | @dot А где поставили | последнюю точку, | вас удивит. ^0.2
@s3 Советский Союз | занимал | @sixth n:шестую n:часть | суши. ^0.2
@s4 Первой ушла | @lt t:Литва. | В @lt2 марте | тысяча девятьсот | девяностого. ^0.2
@s5 В августе | тысяча девятьсот | девяносто первого | @msk в t:Москве | @putsch был r:путч. | @chain После него | началась | цепная реакция. ^0.2
@s6 @ee t:Эстония, | @lv t:Латвия, | @ua t:Украина, | @by t:Беларусь, | @md t:Молдова. | За считанные дни, | одна за другой. ^0.2
@s7 Осенью ушли | @kg t:Кыргызстан, | @uz t:Узбекистан, | @tj t:Таджикистан, | @tm t:Туркменистан. | @cau Ушёл и t:Кавказ. ^0.2
@s8 А t:Казахстан | @wait ждал. | На мартовском | @ref референдуме | @p94 n:девяносто n:четыре n:процента | людей | проголосовали | за сохранение Союза. ^0.2
@s9 Но @d8 n:восьмого n:декабря | @three лидеры России, | Украины и Беларуси | в @bel t:Беловежской t:пуще | объявили, | что СССР | @gone r:больше r:нет. ^0.3
@s10 @d16 n:Шестнадцатого n:декабря | t:Казахстан | объявил @ind t:независимость. | @zh Ровно | через @five n:пять n:лет | после Желтоксана. ^0.3
@s11 А последнюю точку | в истории Союза | поставили | @msk2 не в Москве, | @alm а в t:Алматы. | @d21 n:Двадцать n:первого n:декабря | @n11 n:одиннадцать стран | создали здесь | @cis t:СНГ. | @gorb Через четыре дня | @gk ушёл Горбачёв. ^0.3
@s12 Это бывает @ubt на t:ЕНТ. | @q Когда | провозглашена | независимость | Казахстана? | @ans Ответ: | n:шестнадцатого n:декабря | тысяча девятьсот | девяносто первого. ^0.2
@s13 Перейдите @link по t:ссылке | в шапке профиля.
""",
}
SPOKEN = {'ru': {}, 'kk': {'ҰБТ-да': 'ұбеті', 'ТМД-ны': 'тмдіні'}}
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
    """Cues computed from the word beats; shared by scene.html (picture) and sfx.py (sound).
    Scene 3 is the film shot (Higgsfield), 1, 2, 4, 5, 7 the map, 6 the 1989 crowd, 8 the ENT quiz, 9 the call to action.
    A film shot starts a little before its sentence and takes the pause in front of it."""
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
