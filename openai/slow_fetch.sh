#!/bin/bash
# retry failed thumbs slowly (Wikimedia 429 rate limit)
UA="JasReelsBot/1.0 (https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia; educational video)"
cd "$(dirname "$0")"
while read name hp fn; do
  [ -s photos/$name.jpg ] && continue
  for try in 1 2 3 4 5 6; do
    for s in 960 1280 800 640 500; do
      c=$(curl -s -A "$UA" -o photos/$name.jpg -w "%{http_code}" "https://upload.wikimedia.org/wikipedia/commons/thumb/$hp/$fn/${s}px-$fn")
      [ "$c" = 200 ] && { echo "$name ok $s"; break 2; }
      rm -f photos/$name.jpg; sleep 4
    done
    sleep 30
  done
done <<'L'
dangelo 6/68 Adam_D%27Angelo_-_The_Grove_2022.jpg
garfield c/c6 Andrew_Garfield_at_the_2026_New_York_Film_Festival-18.jpg
taylor 4/4f TechCrunch_Disrupt_2024_D2_Bret_Taylor-3_%28cropped%29.jpg
sutskever d/d4 Ilya_Sutskever_and_Sam_Altman_in_TAU_%28cropped%29.jpg
summers d/d1 Lawrence_Summers_2012_%28cropped%29.jpg
guadagnino 8/80 Luca_Guadagnino_at_the_2026_New_York_Film_Festival-40.jpg
murati b/b1 Guests_at_the_2026_Met_Gala_274_%28Mira_Murati%29.jpg
borisov 6/6c Yura_Borisov_at_the_2026_New_York_Film_Festival-37.jpg
L
echo DONE
