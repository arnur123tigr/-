#!/bin/bash
# fetch overlay photos from Wikimedia Commons (needs a UA with a contact/reuse link; retries on 429)
UA="JasReelsBot/1.0 (https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia; educational video)"
get() { for i in $(seq 1 12); do c=$(curl -s -A "$UA" -o "$1" -w "%{http_code}" "$2"); [ "$c" = 200 ] && { echo "ok $1"; return; }; sleep 15; done; echo "fail $1"; }
get gagarin_portrait.jpg "https://upload.wikimedia.org/wikipedia/commons/5/5b/%D0%9A%D0%BE%D1%81%D0%BC%D0%BE%D0%BD%D0%B0%D0%B2%D1%82_%D0%AE%D1%80%D0%B8%D0%B9_%D0%93%D0%B0%D0%B3%D0%B0%D1%80%D0%B8%D0%BD.jpg"
get aub_stamp.jpg "https://upload.wikimedia.org/wikipedia/commons/9/90/ToktarAwbakirov.jpg"
