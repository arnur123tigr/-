// node record.js out.mp4 [fps]  (LANG_Q=ru|kk) -> silent video of the whole reel (1080x1920).
// Scenes 1 and 6: frames from clips/<lang>/s1|s6/NNNNN.jpg (made by prep_clips.sh) are drawn under the overlays.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const root = __dirname, out = process.argv[2] || 'video_silent.mp4', fps = +(process.argv[3] || 30), L = process.env.LANG_Q || 'ru';
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': ({ '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf', '.jpg': 'image/jpeg', '.png': 'image/png' })[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`http://localhost:${srv.address().port}/scene.html?lang=${L}`); await p.waitForFunction(() => window.ready); await p.evaluate(() => window.ready);
  const { END, S, OFF } = await p.evaluate(() => ({ END: window.END, S: window.S, OFF: window.OFF }));
  const N = Math.round(END * fps);
  const clip = (T) => { // which clip frame (if any) belongs to video time T
    for (const [k, a, z] of [['s1', 0, S[1] + OFF], ['s6', S[5] + OFF, S[6] + OFF]]) if (T >= a && T < z + .4) {
      const dir = path.join(root, 'clips', L, k); if (!fs.existsSync(dir)) return null;
      const n = fs.readdirSync(dir).length, i = Math.min(n, 1 + Math.floor((T - a) * fps)); return `clips/${L}/${k}/${String(i).padStart(5, '0')}.jpg`; }
    return null; };
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', path.join(root, out)], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) {
    const T = i / fps, c = clip(T);
    const url = await p.evaluate(async ([T, c]) => { await setClipFrame(c); render(T); return document.getElementById('c').toDataURL('image/jpeg', 0.94); }, [T, c]);
    if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`frame ${i}/${N}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await b.close(); srv.close(); console.log('done', out, END + 's');
})();
