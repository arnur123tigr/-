"""Kazakh version: words_kk.json (whisper word times of the KK voice) + the script's own spelling -> captions_kk.json,
and tmap_kk.json = [[kk voice time, ru voice time], ...] from ^<ru time> anchors, so the RU-timed animation follows the KK voice.
Alignment is character-level (whisper spells Kazakh loosely and writes numbers as digits)."""
import json, re, difflib
SCRIPT = """^0 Жердің [бүкіл тарихын] | бір ғана [жылға] | сыйғызсақ қайтер еді? | ^3.62 Кеттік! | ^4.56 Бірінші қаңтар, | түн ортасы. | ^6.42 Жер [дүниеге келді!] |
Лавадан жасалған | жарқыраған [шар!] | ^9.42 Бірнеше күннен кейін... | ^10.7 [Бум!] | ^11.34 Алып соқтығыс — | және ^13.0 [Ай] пайда болады. |
^14.12 Наурызда мұхиттарда | алғашқы [кішкентай] | [тірі ағзалар] | пайда болады. | ^18.06 Ал содан кейін | күтеміз... | ^19.82 [күтеміз...] | ^20.76 тағы да [күтеміз!] |
^21.72 Сәуір, мамыр, маусым, | ^23.34 қыркүйек, қазан... | ^24.78 Әлі күнге | бірде-бір [жануар да,] | бірде-бір [ағаш та] жоқ. |
^27.68 Міне, [18 қарашада...] | ^29.68 [Бабах!] | ^30.46 [Кембрий жарылысы!] | ^31.8 Теңіздер кенеттен | [оғаш әрі таңғажайып] | жаратылыстарға толады! |
^35.26 Желтоқсанның басында | балық құрлыққа | ^37.22 алғашқы [қадамын] | жасайды. | ^38.82 11 желтоқсан — | ^40.16 [Ұлы қырылу!] | ^41.44 Әр он түрдің | [тоғызы] жойылып кетеді. |
^43.62 Бірақ 13 желтоқсанда | ^44.92 [динозаврлар] пайда болады! | ^46.86 26 желтоқсанда | ^48.04 [алып астероид] құлайды | ^49.72 және динозаврлар жоғалады. | ^51.52 Жоқ... | бәрі емес. |
^52.78 Құстар — | солардың [шөберелерінің] | [шөберелері!] | ^55.02 Ал біз | қашан пайда [болдық?] | ^56.32 31 желтоқсанда, | түн ортасына | ^58.06 [35 минут] қалғанда! |
^60.12 [1 минут 20 секунд] | қалды — | ^61.96 алғашқы егістіктер. | ^63.02 [36 секунд] — | ^64.16 жазу ойлап табылды. | ^65.52 Бүкіл жазба тарих | басталады. |
^67.86 [2 секундтан] аз қалды — | ^68.92 Америка дүниеге келеді. | ^70.42 Бұл күнтізбеде | ^71.2 1 секунд — | ^72.26 [144 жыл.] | ^74.02 Демек, сенің бүкіл өмірің — | ^75.48 шамамен [жарты секунд!] |
^76.98 [Ойлап көрші:] | ^78.08 динозаврлар | бұл күнтізбеде | ^79.8 тұтас [13 күн] | билік құрды. | ^81.48 Ал бүкіл жазба тарих — | ^83.04 небәрі [36 секунд!] |
^84.46 Айтпақшы, | географиядан ҰБТ-да | ^86.08 мұндай сұрақтар | [өте көп] кездеседі. | ^88.7 [ҰБТ-ға] дайындығыңды | бастағың келсе, | ^90.64 комментарийге | ^91.64 [«+»] деп ^92.6 жаз!"""
SAY = {'18': 'онсегізінші', '11': 'онбірінші', '13': 'онүшінші', '26': 'жиырмаалтыншы', '31': 'отызбірінші', '35': 'отызбес', '1': 'бір', '20': 'жиырма', '36': 'отызалты',
       '2': 'екі', '144': 'жүзқырықтөрт', 'ұбтда': 'ұбэтэда', 'ұбтға': 'ұбэтэға', '«+»': 'плюс'}
def norm(w): return re.sub(r'[^0-9a-zа-яёәғқңөұүһі+«»]', '', w.lower())
def say(w):
    n = norm(w); n2 = n.replace('-', '')
    if n2 in SAY: return SAY[n2]
    if n.startswith('ұбт'): return 'ұбэтэ' + n[3:]
    return re.sub(r'[«»+]', '', n)
chunks, flat = [], []
for ch in SCRIPT.replace('\n', ' ').split('|'):
    toks, hl, anc = [], False, None
    for w in ch.split():
        if w.startswith('^'): anc = float(w[1:]); continue
        if w == '—': toks[-1]['w'] += ' —'; continue
        a = w.startswith('['); b = w.endswith(']'); w = w.strip('[]')
        if a: hl = True
        t = {'w': w, 'h': hl, 'a': anc, 'i': len(flat)}; anc = None; toks.append(t); flat.append(t)
        if b: hl = False
    chunks.append(toks)
# char streams
WN = {'90дың': 'желтоқсанның', '18': 'онсегізінші', '11': 'онбірінші', '13': 'онүшінші', '26': 'жиырмаалтыншы', '31': 'отызбірінші', '35': 'отызбес', '1': 'бір', '20': 'жиырма', '36': 'отызалты', '144': 'жүзқырықтөрт'}
W = json.load(open('words_kk.json'))
wc, wt = [], []
for s, e, w in W:
    n = re.sub(r'[^0-9a-zа-яёәғқңөұүһі]', '', w.lower()); n = WN.get(n, n)
    for k, c in enumerate(n): wc.append(c); wt.append(s + (e - s) * k / max(1, len(n)))
sc, sidx = [], []
for i, t in enumerate(flat):
    for c in say(t['w']): sc.append(c); sidx.append(i)
sm = difflib.SequenceMatcher(None, sc, wc, autojunk=False)
ct = [None] * len(sc)
for blk in sm.get_matching_blocks():
    for k in range(blk.size): ct[blk.a + k] = wt[blk.b + k]
# word start = first matched char time (corrected by char offset), then interpolate the gaps
st = [None] * len(flat)
for j, i in enumerate(sidx):
    if st[i] is None and ct[j] is not None: st[i] = ct[j] - 0.06 * (j - sidx.index(i))
last = -1
for i in range(len(flat)):   # drop matches that jump backwards or far ahead
    if st[i] is not None:
        if st[i] < last or (i + 1 < len(flat) and st[i + 1] is not None and st[i] > st[i + 1] + .1): st[i] = None
        else: last = st[i]
known = [(i, st[i]) for i in range(len(flat)) if st[i] is not None]
for i in range(len(flat)):
    if st[i] is None:
        p = max([k for k in known if k[0] < i], default=(0, 0.0)); n = min([k for k in known if k[0] > i], default=(len(flat), W[-1][1]))
        st[i] = p[1] + (n[1] - p[1]) * (i - p[0]) / (n[0] - p[0]); print('interp', flat[i]['w'], round(st[i], 2))
for i in range(1, len(st)): st[i] = max(st[i], st[i - 1] + 0.05)
out = []
for c in chunks:
    ws = [{'w': t['w'], 'h': t['h'], 's': round(st[t['i']], 2)} for t in c]
    out.append({'s': ws[0]['s'], 'e': 0, 'ws': ws})
for a, b in zip(out, out[1:]): a['e'] = b['s']
out[-1]['e'] = round(W[-1][1] + .6, 2)
for c in out: c['e'] = round(min(c['e'], c['ws'][-1]['s'] + 1.4), 2)
json.dump(out, open('captions_kk.json', 'w'), ensure_ascii=False)
tm = [[round(st[i], 2), t['a']] for i, t in enumerate(flat) if t['a'] is not None]
tm.append([round(W[-1][1] + .3, 2), 93.04 + .3]); tm.append([round(W[-1][1] + 5, 2), 98.0])
end = round(W[-1][1] + OFF_END, 2) if (OFF_END := 0.3 + 1.6) else 0
json.dump({'map': tm, 'end': end}, open('tmap_kk.json', 'w'))
print('end', end); print('\n'.join(f"{c['s']:6.2f} " + ' '.join(('[' + w['w'] + ']') if w['h'] else w['w'] for w in c['ws']) for c in out))
print(tm)
