// node record.js out.mp4 [fps] [from] [to]  -> silent video of the timeline (1080x1920). LANG_Q=ru|kk
// from / to (seconds) record a part only; frames are rendered one by one (render(T) is deterministic) and piped to ffmpeg as JPEG.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const root = __dirname, out = process.argv[2] || 'video_silent.mp4', fps = +(process.argv[3] || 30), lang = process.env.LANG_Q || 'ru';
const MIME = { '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf', '.jpg': 'image/jpeg', '.png': 'image/png', '.bin': 'application/octet-stream' };
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  const end = JSON.parse(fs.readFileSync(path.join(root, 'beats.json')))[lang].end;
  const i0 = Math.round(+(process.argv[4] || 0) * fps), i1 = Math.round(Math.min(end, +(process.argv[5] || end)) * fps);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`http://localhost:${srv.address().port}/scene.html?lang=${lang}`); await p.waitForFunction(() => window.ready, null, { timeout: 180000 });
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', path.join(root, out)], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = i0; i < i1; i++) {
    const url = await p.evaluate(async t => { await prep(t); render(t); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }, i / fps);
    if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - i0) % 150 === 0) console.log(`frame ${i - i0}/${i1 - i0}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await b.close(); srv.close(); console.log('done', out, (i1 - i0) / fps + ' s', ((Date.now() - t0) / 1000).toFixed(0) + ' s');
})();
