// node snap.js t1 t2 ... -> snaps/s_<t>.jpg (video seconds), for checking frames
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname; fs.mkdirSync(path.join(root, 'snaps'), { recursive: true });
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': ({ '.html': 'text/html', '.json': 'application/json', '.svg': 'image/svg+xml', '.ttf': 'font/ttf' })[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } }); p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log(m.text()));
  await p.goto(`http://localhost:${srv.address().port}/scene.html`); await p.evaluate(() => window.ready);
  for (const t of process.argv.slice(2)) { const u = await p.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', .85); }, +t); fs.writeFileSync(path.join(root, 'snaps', `s_${t}.jpg`), Buffer.from(u.split(',')[1], 'base64')); }
  await b.close(); srv.close(); })();
