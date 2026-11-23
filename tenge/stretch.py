"""Quiz pause: the [pause] tag gives ~1.4 s. Insert silence before the answer word so the gap is GAP s.
python3 stretch.py ru|kk -> vo_<lang>.mp3 + words_<lang>.json (shifted). Reads vo_<lang>_raw.mp3, words_<lang>_raw.json."""
import json, subprocess, sys, re
L = sys.argv[1]; GAP = 3.3
W = json.load(open(f'words_{L}_raw.json'))
key = {'ru': 'правил', 'kk': 'д[ұуіи]р'}[L]
j = next(i for i in range(len(W) - 1, 0, -1) if re.match(key, W[i][2].lower()))
a, b = W[j - 1][1], W[j][0]; cut = a + .25; add = round(GAP - (b - a), 2)
print(L, 'gap', round(b - a, 2), 'insert', add, 'at', cut)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'vo_{L}_raw.mp3', '-filter_complex',
  f'[0:a]atrim=0:{cut},asetpts=N/SR/TB[x];[0:a]atrim={cut},asetpts=N/SR/TB[y];anullsrc=r=44100:cl=mono,atrim=0:{add}[s];[x][s][y]concat=n=3:v=0:a=1',
  '-ac', '1', '-ar', '44100', '-b:a', '192k', f'vo_{L}.mp3'], check=True)
W = [[w[0] + add, w[1] + add, w[2]] if w[0] >= cut else w for w in W]
json.dump(W, open(f'words_{L}.json', 'w'), ensure_ascii=False)
