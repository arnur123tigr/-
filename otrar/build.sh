#!/bin/bash
# Assemble the Otrar reel: 8 rendered shots + text overlays + VO/SFX/music.
# usage: ./build.sh <renders_dir> <out_dir>
set -e
cd "$(dirname "$0")"
R=${1:-renders}
O=${2:-build}
mkdir -p "$O"
OFF=$(python3 -c "import json;print(json.load(open('timeline.json'))['vo_offset'])")
TOTAL=$(python3 -c "import json;print(json.load(open('timeline.json'))['total'])")

# 1) overlays
if [ ! -f "$O/ovl/o_0989.png" ]; then python3 overlay.py "$O/ovl"; fi

# 2) shots -> one clip, scaled to 1080x1920, fades after s4 and s7
python3 - "$R" "$O" <<'PY'
import json, sys, subprocess
R, O = sys.argv[1], sys.argv[2]
tl = json.load(open("timeline.json"))["shots"]
inputs, chains = [], []
for i, n in enumerate(["s1","s2","s3","s4","s5","s6","s7","s8"]):
    a, b = tl[n]
    d = b - a
    src = f"{R}/{n}.mp4"
    inputs += ["-i", src]
    f = f"[{i}:v]scale=1080:1920:flags=lanczos,fps=30,setsar=1,trim=duration={d:.3f},setpts=PTS-STARTPTS"
    f += f",tpad=stop_mode=clone:stop_duration=1,trim=duration={d:.3f}"
    if n in ("s4", "s7"):
        f += f",fade=t=out:st={d-0.25:.3f}:d=0.25"
    if n in ("s5", "s8"):
        f += ",fade=t=in:st=0:d=0.25"
    chains.append(f + f"[v{i}]")
fc = ";".join(chains) + ";" + "".join(f"[v{i}]" for i in range(8)) + "concat=n=8:v=1:a=0[cat]"
# gentle grade + soft bloom
fc += ";[cat]split[a][b];[b]curves=all='0/0 0.6/0.55 1/1',gblur=sigma=18[bl];[a][bl]blend=all_mode=screen:all_opacity=0.18,eq=saturation=1.12:contrast=1.04[g]"
cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", fc, "-map", "[g]",
       "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", f"{O}/video_raw.mp4"]
subprocess.run(cmd, check=True)
PY

# 3) overlay text
ffmpeg -y -v error -i "$O/video_raw.mp4" -framerate 30 -i "$O/ovl/o_%04d.png" \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto[v]" -map "[v]" -t "$TOTAL" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p "$O/video.mp4"

# 4) audio: VO dominant, SFX + music ducked under it
python3 sound.py
DMS=$(python3 -c "print(int($OFF*1000))")
mix () {  # $1 = music gain, $2 = out
ffmpeg -y -v error -i audio/vo_a.mp3 -i audio/sfx.wav -i audio/music.wav -filter_complex "
[0:a]aresample=48000,adelay=${DMS}|${DMS},apad,atrim=0:${TOTAL},volume=1.0,asplit[vo][sc];
[1:a]aresample=48000,volume=0.25[sfx];
[2:a]aresample=48000,volume=$1[mus];
[sfx][mus]amix=inputs=2:normalize=0[bed];
[bed][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck];
[vo][duck]amix=inputs=2:normalize=0,alimiter=limit=0.95[m]" -map "[m]" -ac 2 -ar 48000 "$O/tmp_mix.wav"
ffmpeg -y -v error -i "$O/tmp_mix.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2> "$O/ln.txt" || true
python3 - "$O" "$2" <<'PY'
import json, re, sys, subprocess
O, out = sys.argv[1], sys.argv[2]
t = open(f"{O}/ln.txt").read()
j = json.loads(t[t.index("{"):t.rindex("}")+1])
f = ("loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
     "measured_thresh={input_thresh}:offset={target_offset}:linear=true").format(**j)
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{O}/tmp_mix.wav","-af",f,"-ar","48000",out],check=True)
PY
}
mix 0.14 "$O/mix_music.wav"
mix 0.0 "$O/mix_nomusic.wav"

ffmpeg -y -v error -i "$O/video.mp4" -i "$O/mix_music.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$O/otrar_ru.mp4"
ffmpeg -y -v error -i "$O/video.mp4" -i "$O/mix_nomusic.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$O/otrar_ru_no_music.mp4"
ls -la "$O"/otrar_ru*.mp4
