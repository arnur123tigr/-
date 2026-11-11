// node record.js out.mp4 [fps]  -> silent video of the whole timeline (1080x1920)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const root = __dirname, out = process.argv[2] || 'video_silent.mp4', fps = +(process.argv[3] || 30);
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': ({ '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf' })[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  const tl = JSON.parse(fs.readFileSync(path.join(root, 'timeline.json')));
  const dur = +(process.env.VDUR || tl.scenes[tl.scenes.length - 1].end), N = Math.round(dur * fps);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`http://localhost:${srv.address().port}/scene.html?lang=${process.env.VLANG || "ru"}`); await p.waitForFunction(() => window.ready); await p.evaluate(() => window.ready);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path.join(root, out)], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < N; i++) {
    const url = await p.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, i / fps);
    if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`frame ${i}/${N}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await b.close(); srv.close(); console.log('done', out, dur + 's');
})();
