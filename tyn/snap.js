// node snap.js out_dir t1 t2 ...   -> JPEG frames at the given video times (quick preview). LANG_Q=ru|kk, QS=extra query, CAMS='[{...}]' debug cameras
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname, outDir = process.argv[2], times = process.argv.slice(3).map(Number);
const MIME = { '.js': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf', '.jpg': 'image/jpeg', '.png': 'image/png', '.bin': 'application/octet-stream' };
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log('LOG', m.text()));
  const t00 = Date.now();
  await p.goto(`http://localhost:${srv.address().port}/scene.html?lang=${process.env.LANG_Q || 'ru'}${process.env.QS ? '&' + process.env.QS : ''}`);
  await p.waitForFunction(() => window.ready, null, { timeout: 180000 }); console.log('ready', Date.now() - t00, 'ms');
  const cams = process.env.CAMS ? JSON.parse(process.env.CAMS) : null;
  const jobs = cams ? cams.map((c, i) => ({ t: times[0] || 0, c, name: `cam_${i}` })) : times.map(t => ({ t, name: `f_${String(t.toFixed(2)).padStart(6, '0')}` }));
  for (const j of jobs) {
    const t0 = Date.now();
    const url = await p.evaluate(async ({ t, c }) => { if (c) window.setCamQ(c); await render(t); return document.getElementById('c').toDataURL('image/jpeg', .9); }, j);
    fs.writeFileSync(path.join(outDir, j.name + '.jpg'), Buffer.from(url.split(',')[1], 'base64'));
    console.log(j.name, Date.now() - t0, 'ms');
  }
  await b.close(); srv.close();
})();
