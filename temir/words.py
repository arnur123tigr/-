import sys, json, av, numpy as np
from faster_whisper import WhisperModel
f, lang, out = sys.argv[1], sys.argv[2], sys.argv[3]
c = av.open(f); r = av.AudioResampler(format='s16', layout='mono', rate=16000)
a = np.concatenate([fr.to_ndarray().flatten() for p in c.decode(audio=0) for fr in r.resample(p)]).astype(np.float32) / 32768
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, language=lang, word_timestamps=True)
W = [dict(w=x.word.strip(), s=round(x.start, 2), e=round(x.end, 2)) for s in segs for x in s.words]
json.dump(W, open(out, 'w'), ensure_ascii=False)
print(' '.join(f"{w['w']}@{w['s']}" for w in W))
