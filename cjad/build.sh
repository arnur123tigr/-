#!/bin/bash
# Assemble JAS x CJ promo: clips s1 (intro, silent), s2,s3,s4 (talking, 720p lip-sync) + end card; VO + synth beat.
# Inputs in $W: s1.mp4 s2.mp4 s3.mp4 s4.mp4 a1.mp3 a2.mp3 a3.mp3 beat.wav ; endcard.png here.
set -e
W=${W:?}; OUT=${OUT:?}; H=$(cd "$(dirname "$0")" && pwd)
LOGO=/mnt/project-files/references/brand/logo_white_transparent.png
INTRO=${INTRO:-3.2}       # seconds of s1 used before speech
A1=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $W/a1.mp3)
A2=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $W/a2.mp3)
A3=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $W/a3.mp3)
END=3.0
up="scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p"
# 1) video parts, each cut to its voice length (talking clips start at their frame 0 = audio 0)
ffmpeg -v error -y -i $W/s1.mp4 -t $INTRO -vf "$up" -an -c:v libx264 -crf 16 -preset fast $W/p1.mp4
ffmpeg -v error -y -i $W/s2.mp4 -t $A1 -vf "$up" -an -c:v libx264 -crf 16 -preset fast $W/p2.mp4
ffmpeg -v error -y -i $W/s3.mp4 -t $A2 -vf "$up" -an -c:v libx264 -crf 16 -preset fast $W/p3.mp4
ffmpeg -v error -y -i $W/s4.mp4 -t $A3 -vf "$up" -an -c:v libx264 -crf 16 -preset fast $W/p4.mp4
ffmpeg -v error -y -loop 1 -i $H/endcard.png -t $END -vf "zoompan=z='1+0.0006*on':d=1:s=1080x1920:fps=30,format=yuv420p,fade=in:st=0:d=0.35" -c:v libx264 -crf 16 -preset fast $W/p5.mp4
printf "file '%s'\n" $W/p1.mp4 $W/p2.mp4 $W/p3.mp4 $W/p4.mp4 $W/p5.mp4 > $W/list.txt
ffmpeg -v error -y -f concat -safe 0 -i $W/list.txt -c copy $W/body.mp4
TOT=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $W/body.mp4)
T2=$INTRO; T3=$(echo "$INTRO+$A1"|bc -l); T4=$(echo "$T3+$A2"|bc -l); TE=$(echo "$T4+$A3"|bc -l)
# 2) brand layer: small logo top-right while CJ is on screen; captions 2-3 words via drawtext
F=$H/fonts/Montserrat-Black.ttf
cap(){ echo "drawtext=fontfile=$F:text='$1':fontsize=78:fontcolor=$3:borderw=6:bordercolor=black@0.85:x=(w-text_w)/2:y=h*0.70:enable='between(t,$2)'"; }
CAPS="$(cap 'ЙОУ, ПАЦАНЫ!' "$T2,$(echo "$T2+1.6"|bc -l)" white),$(cap 'JAS EDUCATION' "$(echo "$T2+4.4"|bc -l),$T3" '#FEB300'),$(cap 'ПОДГОТОВКА К ЕНТ' "$(echo "$T3+4.2"|bc -l),$(echo "$T3+6.6"|bc -l)" '#FEB300'),$(cap 'РЕАЛЬНО ПОНИМАТЬ' "$(echo "$T3+7.6"|bc -l),$T4" white),$(cap 'ПРОБНЫЙ УРОК' "$(echo "$T4+3.8"|bc -l),$(echo "$T4+5.8"|bc -l)" '#FEB300'),$(cap 'ССЫЛКА В ШАПКЕ' "$(echo "$T4+5.8"|bc -l),$(echo "$T4+7.6"|bc -l)" white)"
ffmpeg -v error -y -i $W/body.mp4 -i $LOGO -filter_complex "[1]scale=-1:80,format=rgba,colorchannelmixer=aa=0.85[lg];[0][lg]overlay=W-w-48:56:enable='lt(t,$TE)',$CAPS,format=yuv420p" -c:v libx264 -crf 17 -preset medium $W/body_brand.mp4
# 3) audio: VO placed at its slots, beat ducked under voice
ffmpeg -v error -y -i $W/a1.mp3 -i $W/a2.mp3 -i $W/a3.mp3 -i $W/beat.wav -filter_complex "\
[0]adelay=$(echo "$T2*1000"|bc -l|cut -d. -f1):all=1[v1];[1]adelay=$(echo "$T3*1000"|bc -l|cut -d. -f1):all=1[v2];[2]adelay=$(echo "$T4*1000"|bc -l|cut -d. -f1):all=1[v3];\
[v1][v2][v3]amix=inputs=3:normalize=0,aresample=44100,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=44100,apad=whole_dur=$TOT,asplit[vo][sc];\
[3]atrim=0:$TOT,volume=${MUSIC_DB:--20}dB[bed];[bed][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[duck];\
[vo][duck]amix=inputs=2:normalize=0,alimiter=limit=0.95,atrim=0:$TOT[a]" -map "[a]" -c:a aac -b:a 192k $W/mix.m4a
ffmpeg -v error -y -i $W/body_brand.mp4 -i $W/mix.m4a -map 0:v -map 1:a -c:v copy -c:a copy -shortest -movflags +faststart $OUT
echo "done $OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT)"
