import ssl, sys, os, asyncio, edge_tts, edge_tts.communicate as cm
cm._SSL_CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
voice, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
rate = sys.argv[4] if len(sys.argv) > 4 else '+0%'
pitch = sys.argv[5] if len(sys.argv) > 5 else '+0Hz'
async def main():
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, proxy=os.environ.get('HTTPS_PROXY'))
    await c.save(out)
asyncio.run(main())
