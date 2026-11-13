// node snap.js t1 t2 ... -> snap_<t>.png (540x960) for checking; OUT=dir
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname; const srv = http.createServer((q, r) => { fs.readFile(path.join(root, decodeURIComponent(q.url.split('?')[0])), (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.end(d); }); }).listen(0);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log('LOG', m.text()));
  await p.goto(`http://localhost:${srv.address().port}/scene.html`); await p.evaluate(() => window.ready);
  for (const t of process.argv.slice(2)) { await p.evaluate(t => render(+t), t); await p.screenshot({ path: path.join(process.env.OUT || root, `snap_${String(t).padStart(6, '0')}.png`) }); }
  await b.close(); srv.close();
})();
