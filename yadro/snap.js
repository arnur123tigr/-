// LANG_Q=ru node snap.js outdir t1 t2 ...  -> PNG frames (540x960 preview scale)
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname, out = process.argv[2], ts = process.argv.slice(3).map(Number), lang = process.env.LANG_Q || 'ru';
const MIME = { '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf', '.jpg': 'image/jpeg', '.png': 'image/png' };
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] }); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log('LOG', m.text()));
  await p.goto(`http://localhost:${srv.address().port}/scene.html?lang=${lang}`); await p.waitForFunction(() => window.ready, null, { timeout: 60000 });
  for (const t of ts) { const t0 = Date.now(); const url = await p.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', .85); }, t); fs.writeFileSync(path.join(out, `f_${t.toFixed(2)}.jpg`), Buffer.from(url.split(',')[1], 'base64')); console.log(t, Date.now() - t0, 'ms'); }
  await b.close(); srv.close();
})();
