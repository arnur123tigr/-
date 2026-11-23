"""Stretch the quiz pause to ~3 s: vo_<L>_raw.mp3 + words_<L>_raw.json -> vo_<L>.mp3 + words_<L>.json.
The silence goes in just before the answer word (Правильно / Дұрыс), found as the first word after the Alps option."""
import json, subprocess, sys, re
L = sys.argv[1]; W = json.load(open(f'words_{L}_raw.json'))
norm = lambda s: re.sub(r'[^\wәғқңөұүһі]', '', s.lower())
ia = max(i for i, w in enumerate(W) if norm(w[2]).startswith(('альп', 'әлпі', 'альпі', 'әлп')))
gap = W[ia + 1][0] - W[ia][1]; add = max(0, 3.0 - gap); cut = W[ia][1] + min(.35, gap / 2)
for w in W[ia + 1:]: w[0] = round(w[0] + add, 2); w[1] = round(w[1] + add, 2)
json.dump(W, open(f'words_{L}.json', 'w'), ensure_ascii=False)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'vo_{L}_raw.mp3', '-filter_complex',
  f'[0:a]aformat=sample_rates=44100:channel_layouts=mono,asplit[x][y];[x]atrim=0:{cut},asetpts=N/SR/TB[a];[y]atrim={cut},asetpts=N/SR/TB[b];aevalsrc=0:d={add:.2f}:s=44100:c=mono[s];[a][s][b]concat=n=3:v=0:a=1',
  '-c:a', 'libmp3lame', '-q:a', '2', f'vo_{L}.mp3'], check=True)
print(L, 'pause', round(gap, 2), '->', round(gap + add, 2), 'at', round(cut, 2))
