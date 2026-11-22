#!/bin/bash
# Wikimedia Commons 960px thumbnails (cloud gets 200 for standard thumb sizes with a reuse-link UA)
UA="JasReelsBot/1.0 (https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia; educational video)"
mkdir -p photos
get() { # name  hashpath  filename(url-encoded)
  for s in 960 500 330; do
    curl -s -A "$UA" -o "photos/$1.jpg" -w "%{http_code}" "https://upload.wikimedia.org/wikipedia/commons/thumb/$2/$3/${s}px-$3" | grep -q 200 && { echo "$1 ok ${s}px"; return; }
    sleep 1
  done; echo "$1 FAIL"; rm -f "photos/$1.jpg"
}
get altman 5/5a "Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg"
get dangelo 6/68 "Adam_D%27Angelo_-_The_Grove_2022.jpg"
get garfield c/c6 "Andrew_Garfield_at_the_2026_New_York_Film_Festival-18.jpg"
get taylor 4/4f "TechCrunch_Disrupt_2024_D2_Bret_Taylor-3_%28cropped%29.jpg"
get shear e/ed "Web_Summit_2018_-_Contentmakers_-_Day_2%2C_November_7_SM7_9280_%2845715722382%29_%28cropped%29.jpg"
get brockman 0/0a "Disrupt_SF_TechCrunch_Disrupt_San_Francisco_2019_-_Day_2_%2848838200316%29_%28cropped%29.jpg"
get barinholtz a/af "Ike_Barinholtz_at_the_2026_New_York_Film_Festival-32_%28cropped%29.jpg"
get sutskever d/d4 "Ilya_Sutskever_and_Sam_Altman_in_TAU_%28cropped%29.jpg"
get summers d/d1 "Lawrence_Summers_2012_%28cropped%29.jpg"
get guadagnino 8/80 "Luca_Guadagnino_at_the_2026_New_York_Film_Festival-40.jpg"
get murati b/b1 "Guests_at_the_2026_Met_Gala_274_%28Mira_Murati%29.jpg"
get barbaro 9/96 "Monica_Barbaro.jpg"
get nadella 7/78 "MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg"
get borisov 6/6c "Yura_Borisov_at_the_2026_New_York_Film_Festival-37.jpg"
