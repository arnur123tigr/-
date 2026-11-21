// node record.js out.mp4 [fps] [from] [to] -> silent 1080x1920 video of the scene (default: all of it, duration = window.END)
// node record.js --snap dir t1 t2 ...    -> preview PNG frames
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const root = __dirname, A = process.argv.slice(2);
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': ({ '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf' })[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log('LOG', m.text()));
  await p.goto(`http://localhost:${srv.address().port}/scene.html?lang=${process.env.LANG_Q || 'ru'}`); await p.waitForFunction(() => window.ready); await p.evaluate(() => window.ready);
  if (A[0] === '--snap') {
    fs.mkdirSync(A[1], { recursive: true });
    for (const t of A.slice(2)) { const u = await p.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', .9); }, +t); fs.writeFileSync(path.join(A[1], `f_${(+t).toFixed(2)}.jpg`), Buffer.from(u.split(',')[1], 'base64')); }
  } else {
    const out = A[0] || 'video_silent.mp4', fps = +(A[1] || 30), dur = await p.evaluate(() => window.END), F0 = Math.round((+(A[2] || 0)) * fps), N = A[3] ? Math.round(+A[3] * fps) : Math.round(dur * fps);
    const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-vf', 'scale=in_range=full:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', path.join(root, out)], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = F0; i < N; i++) {
      const u = await p.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', .93); }, i / fps);
      if (!ff.stdin.write(Buffer.from(u.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 300 === 0) console.log(`frame ${i}/${N}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('done', out, dur + 's');
  }
  await b.close(); srv.close();
})();
