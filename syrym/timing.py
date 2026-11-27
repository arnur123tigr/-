"""Timing for the «Syrym Datuly, 1783-1797» reel (KZ + RU).

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
@s1 Ол n:14 n:жыл | соғысты. | @war r:Патшамен де, | @khan өз t:ханымен де. ^0.2
@s2 Картадан | көрсетемін: | бір батыр | @two n:екі ханның | тағдырын | қалай шешті. | @fin Ал соңы | ешкім күтпеген | жерде бітті. ^0.2
@s3 Бұл — | байбақты руының | старшыны | @syr t:Сырым t:Датұлы. | Ақылы мен | тапқырлығы үшін | оны @bala t:«Бала t:би» | атаған. ^0.2
@s4 @y1782 n:1782-де | патша жарлық | шығарды. | @right Жайықтың | оң жағына | @winter тек t:қыста | және @pay тек t:ақыға | өтуге болады. ^0.2
@s5 @raid r:Жайық r:казактары | даланы шабуды | тоқтатпады. | @nur Ал t:Нұралы t:хан | патшаның қолындағы | @doll r:қуыршаққа айналды. ^0.2
@s6 @y1785 n:1785-те | @n2700 Сырым n:2700 | сарбаз бастап шықты. | @tl t:Тіленші мен t:Барақ | батырлармен бірге | @n6000 n:алты n:мыңнан асты. ^0.2
@s7 Нәтижесі: | @y1786 n:1786-да | t:Нұралы t:хан | Кіші жүзден | біржола қуылып, | @ufa t:Уфаға | жер аударылды. ^0.2
@s8 Орынбор губернаторы | @igel t:Игельстром | хан билігін | @abol мүлде жоюды | ұсынды. | @fail Бірақ бұл реформа | r:іске r:аспады. ^0.2
@s9 @y1792 n:1792-де | Сырым n:мың сарбазбен | @ilek t:Елек қорғанына | шабуыл жасады. | @lose Бұл жолы | r:жеңіліс. ^0.2
@s10 Ал n:1797-де | көтерілісшілер | @esim жаңа хан t:Есімді | @kill r:өлтірді. ^0.2
@s11 Сырым @khiva t:Хиуаға | кетуге мәжбүр болды, | @died сонда | қайтыс болды. | @but Бірақ күресі | бекер кетпеді. | @bank Тыйым салынған | жағалауда | @y1801 n:1801-де | тұтас @bukey t:Бөкей t:Ордасы | пайда болды. ^0.3
@s12 @ubt Бұл t:ҰБТ-да | келеді. | @q Сырым Датұлы | көтерілісі | қай жылдары | болды? | @ans Жауабы: | @years n:1783–97. ^0.2
@s13 Профиль | шапкасындағы | @link t:сілтемеге өтіңіз.
""",
 'ru': """
@s1 n:14 n:лет | он воевал. | @war И с r:царём, | @khan и со своим же t:ханом. ^0.2
@s2 Покажу на карте, | как один батыр | решил судьбу | @two n:двух ханов. | @fin А закончилось всё там, | где никто не ждал. ^0.2
@s3 Это @syr t:Сырым t:Датулы, | старшина | рода байбакты. | За ум и находчивость | его прозвали | @bala t:«Бала t:би». ^0.2
@s4 В @y1782 n:1782-м | вышел царский указ. | @right На правый берег Урала | можно @winter только t:зимой | и @pay только t:за t:плату. ^0.2
@s5 @raid r:Уральские r:казаки | продолжали | набеги на степь. | @nur А хан t:Нуралы | стал @doll r:куклой | в руках царя. ^0.2
@s6 В @y1785 n:1785-м | Сырым вывел | @n2700 n:2700 воинов. | @tl Вместе с отрядами | t:Тленши и t:Барака — | @n6000 больше n:6000. ^0.2
@s7 Итог: | в @y1786 n:1786-м | хана t:Нуралы | навсегда изгнали | из Младшего жуза | и сослали @ufa в t:Уфу. ^0.2
@s8 Оренбургский губернатор | @igel t:Игельстром | предложил вообще | @abol упразднить | власть хана. | @fail Но реформа r:провалилась. ^0.2
@s9 В @y1792 n:1792-м | Сырым с n:тысячей воинов | атаковал @ilek t:Илецкую t:защиту. | @lose На этот раз | r:поражение. ^0.2
@s10 А в n:1797-м | повстанцы @kill r:убили | @esim нового хана t:Есима. ^0.2
@s11 Сырым был вынужден | уйти @khiva в t:Хиву | @died и там умер. | @but Но борьба | была не зря. | @bank На запретном берегу | в @y1801 n:1801-м | появилась целая | @bukey t:Букеевская t:Орда. ^0.3
@s12 @ubt Это бывает | на t:ЕНТ. | @q В какие годы | шло восстание | Сырыма Датулы? | @ans Ответ: | @years n:1783–97. ^0.2
@s13 Перейдите | @link по t:ссылке | в шапке профиля.
""",
}
FIXT = {'ru': {'1783–97.': ('Ответ:', .75)}}
SPOKEN = {'ru': {'ЕНТ.': 'еэнтэ'}, 'kk': {'ҰБТ-да': 'өбәте'}}
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
    """Cues computed from the word beats; shared by scene.html (picture) and sfx.py (sound). Every frame is the map (no film shots)."""
    d = {f'S{i}': m[f's{i}'] - .15 for i in range(2, 14)}
    d['Kill'] = max(m['kill'], m['esim']) + .15            # Esim's portrait goes dark (KZ: name, then verb; RU: verb, then name)
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
    for w, (ref, d) in FIXT.get(lang, {}).items():       # whisper put a long number at the end of its phrase: pin it after the word before
        i = [k for k, x in enumerate(words) if x['w'] == w][-1]; j = [k for k, x in enumerate(words) if x['w'] == ref][-1]; t[i] = t[j] + d
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
