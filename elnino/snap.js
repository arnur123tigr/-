// node snap.js out_dir t1 t2 ... -> PNG frames at given video times (quick preview)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname, outDir = process.argv[2], times = process.argv.slice(3).map(Number);
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': ({ '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf' })[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log('LOG', m.text()));
  await p.goto(`http://localhost:${srv.address().port}/scene.html${process.env.LANG_Q ? '?lang=' + process.env.LANG_Q : ''}`); await p.waitForFunction(() => window.ready); await p.evaluate(() => window.ready);
  for (const t of times) {
    const t0 = Date.now();
    const url = await p.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', .85); }, t);
    fs.writeFileSync(path.join(outDir, `f_${String(t).padStart(6, '0')}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
    console.log(t, Date.now() - t0, 'ms');
  }
  await b.close(); srv.close();
})();
