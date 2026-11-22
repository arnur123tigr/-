# whisper word timestamps for the voice take -> words_kk.json
import json, sys, numpy as np, subprocess
from faster_whisper import WhisperModel
src = sys.argv[1]; out = sys.argv[2]
pcm = subprocess.run(['ffmpeg','-v','error','-i',src,'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
a = np.frombuffer(pcm, np.int16).astype(np.float32)/32768
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, language='kk', word_timestamps=True, beam_size=5)
W = [dict(w=x.word.strip(), s=round(x.start,3), e=round(x.end,3)) for s in segs for x in s.words]
json.dump(W, open(out,'w'), ensure_ascii=False, indent=0); print(len(W))
