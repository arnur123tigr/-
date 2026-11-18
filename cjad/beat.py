# Synthesised laid-back hip-hop beat (no samples), 90 BPM, A minor. Usage: python3 beat.py out.wav seconds
import sys, numpy as np, wave
SR=44100; out=sys.argv[1]; dur=float(sys.argv[2]); bpm=90; beat=60/bpm
N=int(SR*dur); mix=np.zeros(N); rng=np.random.default_rng(7)
def add(sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i<N: mix[i:j]+=sig[:j-i]*g
def kick():
    t=np.arange(int(.45*SR))/SR; f=50+90*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7)
def snare():
    t=np.arange(int(.3*SR))/SR; n=rng.standard_normal(len(t))
    n=np.convolve(n,[1,-1],'same')
    return (0.7*n*np.exp(-t*18)+0.5*np.sin(2*np.pi*185*t)*np.exp(-t*25))
def hat(o=False):
    t=np.arange(int((.25 if o else .06)*SR))/SR; n=rng.standard_normal(len(t))
    n=np.diff(np.concatenate([[0],n]))
    return n*np.exp(-t*(12 if o else 70))
def bass(f,l):
    t=np.arange(int(l*SR))/SR
    s=np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t)
    return np.tanh(1.5*s)*np.minimum(1,t*80)*np.exp(-t*1.2)
def keys(fs,l):
    t=np.arange(int(l*SR))/SR; s=sum(np.sin(2*np.pi*f*t)*np.exp(-t*1.8)+0.25*np.sin(4*np.pi*f*t)*np.exp(-t*4) for f in fs)
    return s*np.minimum(1,t*200)
chords=[[220,261.6,329.6],[174.6,220,261.6],[196,246.9,293.7],[164.8,207.7,246.9]]  # Am F G E
roots=[55,43.65,49,41.2]
bar=4*beat; nb=int(dur/bar)+1
for b in range(nb):
    t0=b*bar; c=b%4
    for k in [0,1.75*beat,2.5*beat]: add(kick(),t0+k,0.9)
    for s in [beat,3*beat]: add(snare(),t0+s+0.02,0.45)
    for h in range(8):
        sw=0.06*beat if h%2 else 0
        add(hat(h==7),t0+h*beat/2+sw,0.12 if h%2 else 0.17)
    add(bass(roots[c],1.6*beat),t0,0.35); add(bass(roots[c],1.0*beat),t0+2.5*beat,0.3)
    add(keys(chords[c],bar),t0,0.09); add(keys([f*2 for f in chords[c][1:]],beat),t0+3*beat+beat/2,0.04)
# vinyl crackle
cr=np.zeros(N); idx=rng.integers(0,N,int(dur*25)); cr[idx]=rng.standard_normal(len(idx))*0.15; mix+=cr
fade=int(1.5*SR); mix[-fade:]*=np.linspace(1,0,fade); mix[:int(.05*SR)]*=np.linspace(0,1,int(.05*SR))
mix=mix/np.max(np.abs(mix))*0.8
st=np.stack([mix,mix],1)
with wave.open(out,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())
