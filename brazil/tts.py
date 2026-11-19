"""Draft voice with free Microsoft voices (edge-tts): RU ru-RU-DmitryNeural, KZ kk-KZ-DauletNeural.
One call per scene, joined with short pauses -> vo_<lang>.mp3 + words_<lang>.json ([t0, t1, word], same format as words.py).
Usage: python3 tts.py ru|kk"""
import asyncio, json, ssl, subprocess, sys, os
import edge_tts, edge_tts.communicate as EC
EC._SSL_CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
L = sys.argv[1]
VOICE = {'ru': 'ru-RU-DmitryNeural', 'kk': 'kk-KZ-DauletNeural'}[L]
S = json.load(open('vo_text.json'))[L]   # spoken text per scene (ЕНТ / ҰБТ spelled out for the TTS)
GAP = .3
async def one(text, out):
    c = edge_tts.Communicate(text, VOICE, rate='+22%', pitch='+2Hz', boundary='WordBoundary'); ws = []
    with open(out, 'wb') as f:
        async for ch in c.stream():
            if ch['type'] == 'audio': f.write(ch['data'])
            elif ch['type'] == 'WordBoundary': ws.append([ch['offset'] / 1e7, (ch['offset'] + ch['duration']) / 1e7, ch['text']])
    return ws
os.makedirs('tmp_tts', exist_ok=True); W = []; t = 0.; parts = []
for i, s in enumerate(S):
    f = f'tmp_tts/{L}_{i}.mp3'; ws = asyncio.run(one(s, f))
    wav = f'tmp_tts/{L}_{i}.wav'; subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f, '-ar', '48000', '-ac', '1', wav], check=True)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav], capture_output=True, text=True).stdout)
    W += [[round(a + t, 2), round(b + t, 2), w] for a, b, w in ws]; parts.append(wav); t += d + GAP
with open('tmp_tts/list.txt', 'w') as f:
    for p in parts: f.write(f"file '{os.path.basename(p)}'\nfile 'gap.wav'\n")
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=mono', '-t', str(GAP), 'tmp_tts/gap.wav'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'tmp_tts/list.txt', '-b:a', '192k', f'vo_{L}.mp3'], check=True)
json.dump(W, open(f'words_{L}.json', 'w'), ensure_ascii=False); print(L, round(t, 2), 's,', len(W), 'words')
