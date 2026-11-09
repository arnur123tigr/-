# words_b.json (whisper) -> captions.json: 1-4 word chunks at the top, spelling fixed to match the script.
import json, re
W = json.load(open('words_b.json'))
FIX = {'все': 'всё', 'идет': 'идёт', 'растет.': 'растёт.', 'путем.': 'путём.', 'продает': 'продаёт', 'Аналог,': 'А налог,',
       'прибыли.': 'прибыли?', 'самая': 'самое', 'худшая.': 'худшее.', 'ему': 'им', 'плыть.': 'уплыть.', 'ENT': 'ЕНТ', 'ENT.': 'ЕНТ.',
       '«Гео».': '«гео».', '2': 'два', 'вообще.': 'вообще.', 'цента': 'цента', 'долларов,': 'долларов.', 'а': 'А', 'больше,': 'больше'}
words = []
for i, (s, e, w) in enumerate(W):
    w = FIX.get(w, w)
    if w == 'долларов.' and i != 15: w = 'долларов'
    if w == 'А' and i not in (16, 67, 133): w = 'а'
    words.append([s, e, w])
words[13][2] = '2'; words[14][2] = 'триллиона'; words[15][2] = 'долларов.'; words[118][2] = 'цента —'
words[16][2] = 'А'; words[133][2] = 'а'; words[138][0] = 59.13
caps, cur = [], []
def flush():
    if cur: caps.append({'s': cur[0][0], 'e': cur[-1][1], 't': ' '.join(w[2] for w in cur)})
for i, w in enumerate(words):
    cur.append(w)
    n = sum(len(x[2]) for x in cur)
    nxt = words[i + 1] if i + 1 < len(words) else None
    end = re.search(r'[.,?!»]$', w[2]) or n > 16 or len(cur) >= 4 or (nxt and nxt[0] - w[1] > .35)
    if end: flush(); cur = []
flush()
for i in range(len(caps) - 1): caps[i]['e'] = min(caps[i + 1]['s'], max(caps[i]['e'], caps[i]['s'] + .45))
json.dump(caps, open('captions.json', 'w'), ensure_ascii=False)
for c in caps: print(f"{c['s']:6.2f}-{c['e']:6.2f} {c['t']}")
