"""Free draft voice (Microsoft Edge neural TTS): python3 etts.py text.txt voice out.mp3 [rate]"""
import asyncio, ssl, sys, aiohttp, edge_tts
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
import edge_tts.communicate as _c; _c._SSL_CTX = ctx
txt, voice, out = sys.argv[1:4]; rate = sys.argv[4] if len(sys.argv) > 4 else '+8%'
asyncio.run(edge_tts.Communicate(open(txt).read().strip(), voice, rate=rate).save(out))
