"""Timing for the «Миллион қазақ шекарадан қашты» reel (KZ + RU).

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
TAIL = 2.8          # video keeps running after the last word (the end card: logo + call to action)
SCRIPT = {
 'kk': """
@s1 Бір @mil n:миллион n:қазақ | өз жерінен | жаяу қашты. | Ал жау | шапқан жоқ. ^0.2
@s2 Олар @where қайда кетті? | Неге көбі | қайтпады? | Үш бағытты | көрсетемін. | Үшіншісі | r:ең r:ауыр. ^0.5
@s3 n:1932 жыл. | Ауылдарда | мал да, нан да | r:қалмаған. ^0.5
@s4 n:1929 жылы | қазақта | @m40 n:40 n:миллион мал | болған. | @y4 Төрт жылдан кейін — | @m45 n:4,5 n:миллион | ғана. ^0.3
@s5 Мұны | жау емес, | @power r:өз r:билігі | жасады. | @gol Голощекиннің | @kq t:«Кіші t:Қазан» | саясаты | @take малды | тартып алып, | көшпелі халықты | күштеп | отырықшы етті. ^0.4
@s6 @r1 Бірінші жол — | @east t:шығысқа. | Таудан асып, | @cn t:Қытай мен | @mn t:Моңғолияға. ^0.3
@s7 @r2 Екінші жол — | @south t:оңтүстікке. | Құм арқылы | @af t:Ауғанстан мен | @ir t:Иранға, | @far кейін | одан да әрі. ^0.3
@s8 @r3 Үшінші жол — | көрші | @rep республикаларға. | @but Бірақ шекарада | оларды көбіне | r:әскер күтіп тұрды. | @shot Талай адам | сол жерде | r:оққа r:ұшты. ^0.5
@s9 Кеткендердің | @k616 n:600 n:мыңнан астамы | @noret r:қайтып r:оралмады. | @shym Бұл бүгінгі | t:Шымкент халқының | жартысындай. ^0.5
@s10 Ал қалғандары | @hunger r:аштан r:өлді. | @m15 n:1,5 n:миллионнан | астам адам. ^0.6
@s11 Сөйтіп қазақ | @y13 n:13 жылдың ішінде | өз жерінде | @minor r:азшылыққа айналды. | @y30 Бұрынғы санына | қайта жету үшін | халыққа | n:30 n:жылдан астам | уақыт керек болды. ^0.5
@s12 Бұл @ubt t:ҰБТ-да келеді. | @q «Кіші Қазан» | саясатын | кім жүргізді? ^0.5 | @ans Жауабы — | t:Филипп t:Голощекин. ^0.2 | @may Ал n:31 n:мамыр — | сол құрбандарды | еске алу күні. ^0.4
@s13 Тарихты | ұмытпау үшін | профиль шапкасындағы | @link t:сілтемеге өтіңіз.
""",
 'ru': """
@s1 @mil n:Миллион n:казахов | пешком бежали | со своей земли. | А враг | не нападал. ^0.2
@s2 Куда @where они ушли? | Почему многие | не вернулись? | Покажу три | направления. | Третье — | r:самое r:тяжёлое. ^0.5
@s3 n:1932. ^0.2 | В аулах | не осталось | ни скота, | ни хлеба. ^0.5
@s4 В n:1929 | у казахов было | @m40 n:40 n:миллионов | голов скота. | @y4 Через 4 года — | @m45 всего n:4,5. ^0.3
@s5 Это сделал | не враг, | @power а r:своя r:власть. | Политика | @kq t:«Малого t:Октября» | @gol Голощёкина | @take отобрала скот | и силой заставила | кочевников осесть. ^0.4
@s6 @r1 Первый путь — | @east t:на t:восток. | Через горы, | @cn в t:Китай | @mn и t:Монголию. ^0.3
@s7 @r2 Второй путь — | @south t:на t:юг. | Через пески | @af в t:Афганистан | @ir и t:Иран, | @far а потом | ещё дальше. ^0.3
@s8 @r3 Третий путь — | @rep в соседние республики. | @but Но на границе | их часто | r:ждали r:войска. | @shot Многие погибли | прямо там. ^0.5
@s9 Больше | @k616 n:600 n:тысяч ушедших | @noret r:так r:и r:не r:вернулись. | @shym Это как половина | сегодняшнего t:Шымкента. ^0.5
@s10 А оставшиеся | @hunger r:умирали r:от r:голода. | @m15 Больше n:полутора n:миллионов | человек. ^0.6
@s11 Так, | @y13 за n:13 лет | казахи стали | @minor r:меньшинством | на своей земле. | @y30 Чтобы вернуться | к прежней численности, | народу понадобилось | больше n:30 n:лет. ^0.5
@s12 Это бывает @ubt на t:ЕНТ. | @q Кто проводил | политику | «Малого Октября»? ^0.5 | @ans Ответ — | t:Филипп t:Голощёкин. ^0.2 | @may А n:31 n:мая — | день памяти | этих жертв. ^0.4
@s13 Чтобы помнить историю, | перейдите @link по t:ссылке | в шапке профиля.
""",
}
SPOKEN = {'ru': {'ЕНТ.': 'ент', 'Голощёкина': 'голощокина', 'Голощёкин.': 'голощокин'},
          'kk': {'ҰБТ-да': 'өбәтедә', 'Төрт': '4', '4,5': '4жарым', '1,5': '1жарым', 'Голощекиннің': 'галашекиннің', 'Голощекин.': 'галашекин'}}
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
