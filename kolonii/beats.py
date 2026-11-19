"""Beat times (voice seconds after atempo 1.08, read from whisper words_ru.json) -> beats.json."""
import json
B = dict(q=0, y250=1.82, apart=5.54, crown=10.32, war=11.98, beat=14.3, lands=15.86, debt=17.98, look=21.6, prot=24.16, pay=25.72, sugar=26.62, molasses=29.08,
         sugarI=29.72, coffee=30.2, cloth=30.96, angry=31.7, stamp=33.34, news=37.68, contr=38.3, lic=38.92, court=39.58, cards=41.14, congr=42.32, parl=45.58,
         taxes=48.7, angry2=50.38, boston=51.9, shoot=55.2, dead=56.22, massacre=57.94, cancel=60.02, teatax=63.8, tea=66.12, dump=70.08, n300=71.02, party=73.0,
         fury=74.96, port=76.44, self=77.96, troops=79.26, cc1=80.9, lex=83.82, shot=89.34, warb=91.08, wash=92.64, washn=94.8, peace=95.98, refuse=98.92,
         july=100.2, decl=104.66, equal=108.56, usa=113.5, cta=117.8, link=119.2, vend=121.0)
json.dump({'ru': B}, open('beats.json', 'w'), indent=0)
