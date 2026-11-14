#!/bin/bash
# Retime the two 5-s Higgsfield clips to each language's scene length (motion-interpolated) and dump 1080x1920 JPEG frames.
set -e; cd "$(dirname "$0")"
for L in ru kk; do
  read D1 D6 < <(node -e "
    const s=require('fs').readFileSync('scene.html','utf8').split('  $L: {')[1]; const S=JSON.parse(s.match(/S: (\[[^\]]+\])/)[1]);
    console.log((S[1]+0.3+0.4).toFixed(3), (S[6]-S[5]+0.4).toFixed(3))")
  for k in s1 s6; do
    D=$([ $k = s1 ] && echo $D1 || echo $D6); SRC=clip_$k.mp4; [ -f $SRC ] || continue
    SD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $SRC); F=$(python3 -c "print($D/$SD)")
    rm -rf clips/$L/$k; mkdir -p clips/$L/$k
    ffmpeg -loglevel error -y -i $SRC -vf "setpts=$F*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -q:v 2 clips/$L/$k/%05d.jpg
    echo "$L $k: $D s (x$F), $(ls clips/$L/$k | wc -l) frames"
  done
done
