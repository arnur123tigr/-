#!/bin/bash
# usage: ./build_final.sh path/to/cta.mp3   -> baitursynov_ru.mp4 with the "25" call to action
set -e
cd "$(dirname "$0")"
cp "$1" vo_cta.mp3
CTA=$(ffprobe -v error -show_entries format=duration -of csv=p=0 vo_cta.mp3)
CUT=29.46; GAP=0.3
END=$(python3 -c "print(round($CUT+$GAP+$CTA+0.7,2))")
ffmpeg -loglevel error -y -i vo_ru.mp3 -i vo_cta.mp3 -filter_complex \
 "[0:a]aresample=48000,atrim=0:$CUT,afade=t=out:st=$(python3 -c "print($CUT-0.08)"):d=0.08[a];[1:a]aresample=48000,adelay=$(python3 -c "print(int($GAP*1000))")|$(python3 -c "print(int($GAP*1000))")[b];[a][b]concat=n=2:v=0:a=1[o]" -map "[o]" vo_full.wav
python3 - "$END" <<'PY'
import json,sys
tl=json.load(open('timeline.json')); tl['voiceover']='vo_full.wav'; tl['scenes'][-1]['end']=float(sys.argv[1])
json.dump(tl,open('timeline.json','w'),indent=1)
PY
python3 sfx.py
node record.js video_silent.mp4 | tail -1
ffmpeg -loglevel error -y -i video_silent.mp4 -i vo_full.wav -i sfx.wav -filter_complex "[1:a]aresample=48000[v];[2:a]volume=0.7[s];[v][s]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t $END baitursynov_ru.mp4
echo "built $END s"
