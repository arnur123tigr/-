#!/bin/bash
# Re-record only the two photo windows (scenes 2 and 6) and splice them into an existing silent recording.
# ./patch_photos.sh ru 9.5 14.7 35.0 42.2
set -e
cd "$(dirname "$0")"
L=$1; A0=$2; A1=$3; B0=$4; B1=$5; V=video_silent_$L.mp4
LANG_Q=$L node record.js part_a_$L.mp4 30 $A0 $A1
LANG_Q=$L node record.js part_b_$L.mp4 30 $B0 $B1
f() { python3 -c "print(round($1*30))"; }
a0=$(f $A0); a1=$(f $A1); b0=$(f $B0); b1=$(f $B1)
ffmpeg -v error -y -i $V -i part_a_$L.mp4 -i part_b_$L.mp4 -filter_complex "
[0:v]trim=end_frame=$a0,setpts=PTS-STARTPTS[v0];[0:v]trim=start_frame=$a1:end_frame=$b0,setpts=PTS-STARTPTS[v1];[0:v]trim=start_frame=$b1,setpts=PTS-STARTPTS[v2];
[v0][1:v][v1][2:v][v2]concat=n=5:v=1[v]" -map "[v]" -r 30 -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p patched_$L.mp4
ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $V patched_$L.mp4 2>/dev/null || true
mv $V orig_$V; mv patched_$L.mp4 $V; rm -f part_a_$L.mp4 part_b_$L.mp4
