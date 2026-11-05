// node snap.js t1 t2 ... -> stills/t.png
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname;
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': ({ '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf' })[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] }); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`http://localhost:${srv.address().port}/scene.html`); await p.waitForFunction(() => window.ready); await p.evaluate(() => window.ready);
  fs.mkdirSync(path.join(root, 'stills'), { recursive: true });
  for (const t of process.argv.slice(2)) {
    const url = await p.evaluate(t => { render(+t); return document.getElementById('c').toDataURL('image/jpeg', .85); }, t);
    fs.writeFileSync(path.join(root, 'stills', `${t}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
  }
  await b.close(); srv.close();
})();
