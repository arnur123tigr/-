# shorten pauses in the voice take to at most MAXG s, then speed up slightly -> vo_kk.mp3
import subprocess, re, sys, numpy as np, wave
MAXG, TEMPO = 0.30, 1.04
src, out = 'vo_kk_take.mp3', 'vo_kk.mp3'
e = subprocess.run(['ffmpeg','-i',src,'-af','silencedetect=n=-42dB:d=0.32','-f','null','-'],capture_output=True,text=True).stderr
S = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', e)]; E = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', e)]
pcm = subprocess.run(['ffmpeg','-v','error','-i',src,'-f','s16le','-ac','1','-ar','48000','-'],capture_output=True).stdout
a = np.frombuffer(pcm, np.int16); sr = 48000; keep = []; pos = 0
for s, en in zip(S, E):
    if s < 0.05: pos = int(max(0, en - 0.05) * sr); continue
    cut0 = s + MAXG / 2; cut1 = en - MAXG / 2
    if cut1 > cut0: keep.append(a[pos:int(cut0 * sr)]); pos = int(cut1 * sr)
keep.append(a[pos:]); b = np.concatenate(keep)
with wave.open('/tmp/vo_t.wav','wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(b.tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i','/tmp/vo_t.wav','-af',f'atempo={TEMPO}','-b:a','192k',out])
print('in', len(a)/sr, 'trimmed', len(b)/sr, 'out', len(b)/sr/TEMPO)
