import sys, json, subprocess, numpy as np
from faster_whisper import WhisperModel
raw = subprocess.run(['ffmpeg','-loglevel','error','-i',sys.argv[1],'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
a = np.frombuffer(raw,np.int16).astype(np.float32)/32768
m = WhisperModel('small', compute_type='int8')
segs,_ = m.transcribe(a, language=sys.argv[3] if len(sys.argv)>3 else "ru", word_timestamps=True)
W=[]
for s in segs:
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
    W += [[round(w.start,2), round(w.end,2), w.word.strip()] for w in s.words]
json.dump(W, open(sys.argv[2],'w'), ensure_ascii=False)
