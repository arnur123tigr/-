"""Timing for the Atacama reel (KZ + RU).

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
@s1 Бұл қалада | @yrs n:14 жыл бойы | бір тамшы @rain жаңбыр | r:жаумаған. ^0.2
@s2 Ең қызығы — | қала @ocean t:мұхиттың | дәл жағасында тұр. ^0.2
@s3 Бұл — @ata t:Атакама, | Жердегі | ең құрғақ | шөлдердің бірі. | @three Оны n:үш нәрсе | жасаған. ^0.2
@s4 Бірінші: | жағаның бойымен | @cur суық t:Перу t:ағысы | жүреді. | @cold Суық су | бұлтқа | ылғал r:бермейді. ^0.2
@s5 Екінші: | шығыстағы | @clouds ылғалды бұлттарды | @andes t:Анд таулары | тосып қалады. | @rainE Жаңбырдың бәрі | арғы бетке жауады. ^0.2
@s6 Үшінші: | бұл жерде | @hp t:жоғары t:қысым тұрады. | @down Ауа жоғарыдан | төмен түседі де, | @nocl бұлт r:түзілмейді. ^0.2
@s7 Топырағы | @mars t:Марсқа | ұқсайтыны сонша, | @nasa NASA | өз роверлерін | осында сынаған. ^0.2
@s8 Ал көлемі | шамамен | @pav t:Павлодар | облысындай. ^0.3
@s9 Бірақ кейде, | бірнеше жылда | бір рет | @drop жаңбыр жауса, | осы өлі шөл | @bloom миллиондаған | t:гүлге оранады. ^0.2
@s10 Тұқым | жылдар бойы | топырақта жатып, | @wait жаңбырды күтеді. ^0.3
@s11 Бұл @ubt t:ҰБТ-да келеді. | @q Атакама шөлінің | пайда болуына | қандай ағыс | әсер етті? | @ans Жауабы: | t:суық t:Перу t:ағысы. ^0.2
@s12 Профиль шапкасындағы | @link t:сілтемеге өтіңіз.
""",
 'ru': """
@s1 В этом городе | @yrs n:14 лет | не выпало | @rain ни капли r:дождя. ^0.2
@s2 И самое странное — | город стоит | прямо на берегу | @ocean t:океана. ^0.2
@s3 Это @ata t:Атакама — | одна из самых | сухих пустынь | на Земле. | @three Её создали | n:три вещи. ^0.2
@s4 Первая: | вдоль берега идёт | @cur холодное t:Перуанское t:течение. | @cold Холодная вода | почти не даёт | влаги облакам. ^0.2
@s5 Вторая: | @clouds влажные облака | с востока | задерживают @andes t:Анды. | @rainE Весь дождь | выпадает | на другой стороне. ^0.2
@s6 Третья: | здесь стоит | @hp область t:высокого t:давления. | @down Воздух опускается | сверху, | @nocl и облака r:не r:образуются. ^0.2
@s7 Почва здесь | так похожа | на @mars t:марсианскую, | что @nasa NASA | испытывало тут | свои роверы. ^0.2
@s8 А размером | она примерно | как @pav t:Павлодарская | область. ^0.3
@s9 Но иногда, | раз в несколько лет, | @drop проходит дождь — | и эта мёртвая пустыня | @bloom покрывается | миллионами t:цветов. ^0.2
@s10 Семена | годами лежат | в земле | @wait и ждут дождя. ^0.3
@s11 Это бывает @ubt на t:ЕНТ. | @q Какое течение | повлияло | на образование | пустыни Атакама? | @ans Ответ: | t:холодное t:Перуанское t:течение. ^0.2
@s12 Перейдите | @link по t:ссылке | в шапке профиля.
""",
}
SPOKEN = {'ru': {'NASA': 'наса'}, 'kk': {'ҰБТ-да': 'үбетеде', 'келеді.': 'келет', 'NASA': 'наса'}}
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
    d = {f'S{i}': m[f's{i}'] - .15 for i in range(2, 13)}
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
