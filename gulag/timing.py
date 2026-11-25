"""Timing for the GULAG reel (KZ + RU).

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
@s1 Сталин ең қорқынышты | лагерлерін неге | дәл @our біздің далаға | салды? ^0.3
@s2 @three Үш лагерді | көрсетемін. | Үшіншісінде | @simple қарапайым қазақтар | ешкім ұмытпайтын | іс жасады. ^0.3
@s3 Жауабы қарапайым. | @coal Жер астында t:көмір~ | t:мен @cu t:мыс бар. | @msk Ал Мәскеуден | n:мыңдаған шақырым. | @run Қашатын жер жоқ. ^0.3
@s4 Бірінші — | @karlag t:Қарлаг. | @len Солтүстіктен оңтүстікке | n:300 шақырым. | @ast Астана мен Қарағанды | арасынан да ұзын. ^0.3
@s5 @dep Лагерлерден бөлек, | бұл жерге тұтас халықтар | жер аударылды. | @kor Кәрістер, | @ger немістер, | @che шешендер. | @mln n:Миллионнан астам адам. ^0.3
@s6 Екінші — | @step t:Степлаг. | @y54 n:1954 жылы | @keng Кеңгірде тұтқындар | r:көтеріліп, | @d40 n:40 күн ұстап тұрды. | @tank Көтерілісті | r:танкімен басты. ^0.3
@s7 Үшінші — | @alzh t:АЛЖИР. | @km35 Бүгінгі Астанадан | небәрі n:35 шақырым жерде. ^0.2
@s8 Мұнда «халық жауларының» | әйелдері отырды. | @k18 n:18 мыңдай әйел. | @guilt Кінәсі — | тек күйеуі. ^0.3
@s9 Олардың арасында | @gul Сәкен Сейфуллиннің жары | t:Гүлбаһрам да болды. | @kids Балаларын қолынан | тартып алып, | балалар үйіне жіберді. ^0.3
@s10 Бірде қоршаудың сыртынан | бірдеңе ұшып келді. | @stone Әйелдер оны | тас деп ойлады. ^0.4
@s11 @kurt Бұл тас емес, | t:құрт еді. | @aul Жақын ауылдың қазақтары | өздері аш бола тұра, | тұтқын әйелдерге | тамақ лақтырды. | @kind Түрменің ортасында да | қазақ даласы | t:мейірімді болып қалды. ^0.4
@s12 Бұл @ubt t:ҰБТ-да келеді. | @q АЛЖИР дегеніміз не? | @ans Жауабы — | Отанын сатқандардың | әйелдеріне арналған | t:Ақмола t:лагері. | @may Ал n:31 n:мамыр — | қуғын-сүргін құрбандарын | еске алу күні. ^0.3
@s13 Тарихты осылай | білгің келсе, | профиль шапкасындағы | @link t:сілтемеге өтіңіз.
""",
 'ru': """
@s1 Почему Сталин построил | самые страшные лагеря | именно @our в нашей степи? ^0.3
@s2 @three Покажу три лагеря. | В третьем | @simple простые казахи | сделали то, | что никто не забыл. ^0.3
@s3 Ответ простой. | @coal Под землёй t:уголь | @cu и t:медь. | @msk А до Москвы | n:тысячи километров. | @run Бежать некуда. ^0.3
@s4 Первый — | @karlag t:Карлаг. | @len С севера на юг | n:300 километров. | @ast Длиннее, чем | от Астаны до Караганды. ^0.3
@s5 @dep Кроме лагерей, | сюда ссылали | целые народы. | @kor Корейцы, | @ger немцы, | @che чеченцы. | @mln n:Больше n:миллиона человек. ^0.3
@s6 Второй — | @step t:Степлаг. | @y54 В n:1954 | @keng в Кенгире | заключённые r:восстали | @d40 и держались n:40 дней. | @tank Восстание | r:раздавили r:танками. ^0.3
@s7 Третий — | @alzh t:АЛЖИР. | @km35 Всего в n:35 километрах | от сегодняшней Астаны. ^0.2
@s8 Здесь сидели | жёны «врагов народа». | @k18 Около n:18 тысяч женщин. | @guilt Их вина — | только муж. ^0.3
@s9 Среди них была | @gul и жена Сакена Сейфуллина, | t:Гульбахрам. | @kids Детей у них отбирали | и отправляли в детдома. ^0.3
@s10 Однажды из-за забора | что-то полетело. | @stone Женщины подумали, | что это камни. ^0.4
@s11 @kurt Это были не камни, | а t:курт. | @aul Казахи из соседнего аула, | сами голодая, | бросали узницам еду. | @kind Даже посреди тюрьмы | казахская степь | t:осталась t:доброй. ^0.4
@s12 Это бывает @ubt на t:ЕНТ. | @q Что такое АЛЖИР? | @ans Ответ — | t:Акмолинский t:лагерь | жён изменников Родины. | @may А n:31 n:мая — | день памяти | жертв репрессий. ^0.3
@s13 Хотите знать историю так — | перейдите @link по t:ссылке | в шапке профиля.
""",
}
SPOKEN = {'ru': {}, 'kk': {}}
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
