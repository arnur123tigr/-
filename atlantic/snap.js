// node snap.js out.jpg t1 t2 ... -> contact sheet of frames at voice times (for checking)
const { chromium } = require('playwright'); const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname; const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200); r.end(d); }); }).listen(0);
(async () => {
  const [out, ...ts] = process.argv.slice(2); const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log('LOG', m.text()));
  await p.goto(`http://localhost:${srv.address().port}/scene.html`); await p.waitForFunction(() => window.ready); await p.evaluate(() => window.ready);
  const n = ts.length, cols = Math.min(n, 6), rows = Math.ceil(n / cols);
  const urls = []; for (const t of ts) urls.push(await p.evaluate(t => { render(t + 0.3); return document.getElementById('c').toDataURL('image/jpeg', .8); }, +t));
  await p.setContent(`<body style="margin:0;background:#000;width:${cols * 270}px">${urls.map((u, i) => `<div style="position:relative;display:inline-block;width:270px;height:480px"><img src="${u}" style="width:270px;height:480px"><span style="position:absolute;top:2px;left:4px;color:#ff0;font:bold 16px sans-serif;background:#000a">${ts[i]}</span></div>`).join('')}</body>`);
  await p.setViewportSize({ width: cols * 270, height: rows * 484 }); await p.screenshot({ path: out, fullPage: true }); await b.close(); srv.close();
})();
