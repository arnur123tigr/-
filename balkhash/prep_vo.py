"""Stretch the quiz pause to 3 s: insert silence between the answer options and «Правильно/Дұрыс».
vo_<lang>.mp3 + words_<lang>.json -> vo_<lang>_x.wav + words_<lang>_x.json. Usage: python3 prep_vo.py ru|kk"""
import sys, json, subprocess
L = sys.argv[1]; W = json.load(open(f'words_{L}.json'))
key = {'ru': 'Правильно', 'kk': 'Дұр'}[L]
lead = max(0, round(W[0][0] - .05, 3)); W = [[w[0] - lead, w[1] - lead, w[2]] for w in W]   # trim leading silence
i = max(j for j, w in enumerate(W) if w[2].strip(',.–-—').startswith(key[:3]))
a, b = W[i - 1][1], W[i][0]; ins = max(0, 3.0 - (b - a)); cut = round((a + b) / 2, 3)
print('lead', lead, 'pause', a, b, 'insert', round(ins, 2), 'at', cut)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'vo_{L}.mp3', '-filter_complex',
                f'[0:a]atrim={lead}:{cut + lead},asetpts=N/SR/TB[a];[0:a]atrim={cut + lead},asetpts=N/SR/TB[b];aevalsrc=0:d={ins:.3f}:s=44100[s];[a][s][b]concat=n=3:v=0:a=1',
                '-ar', '48000', '-ac', '1', f'vo_{L}_x.wav'], check=True)
json.dump([[w[0] + (ins if w[0] > cut else 0), w[1] + (ins if w[0] > cut else 0), w[2]] for w in W], open(f'words_{L}_x.json', 'w'), ensure_ascii=False)
