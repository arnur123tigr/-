"""Beat times (voice seconds, read from whisper words_ru.json) -> beats.json."""
import json
B = dict(q=0, usa=.34, can=1.18, gl=1.94, what=3.32, five=5.12, sup=6.32, mic=7.02, hur=7.74, eri=8.36, ont=8.84, pct=9.6, n20=10.48, vol=13.66, n23=14.12,
         hard=16.86, spread=18.06, am=21.0, af=21.74, eu=22.26, au=22.88, an=23.86, cm=24.8, n15=26.94, big=28.28, oth=32.5, aut=33.58, cze=34.7, irl=35.36,
         pan=36.02, bal=36.86, n5=38.72, sea=39.7, shore=42.06, storm=44.32, wave=46.98, ships=48.22, n350=50.1, ef=51.92, conn=54.18, law=56.58, atl=59.3,
         ppl=60.6, n40=61.84, sp=63.4, n4000=64.24, great=66.9, grt2=68.54, cta=69.48, link=70.92, vend=72.6)
json.dump({'ru': B}, open('beats.json', 'w'), indent=0)
