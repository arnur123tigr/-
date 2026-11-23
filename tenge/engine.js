// Shared 2D map engine for the remake reels: equirectangular Blue Marble textures drawn under a moving camera,
// vector overlays in lon/lat, cards, labels, pills, CTA and the JAS end card. Deterministic: everything is a function of t.
const W = 1080, H = 1920;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const ctx = cv.getContext('2d');
const BR = { navy: '#130B54', acc: '#FEB300', white: '#FFFFFF', red: '#E8502F' };
const IM = {};
const loadImg = (k, src) => new Promise((ok, no) => { const i = new Image(); i.onload = () => { IM[k] = i; ok(); }; i.onerror = () => no(src); i.src = src; });
const loadFont = (fam, src, w) => new FontFace(fam, `url(${src})`, { weight: w || 'normal' }).load().then(f => document.fonts.add(f));
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, k) => a + (b - a) * k;
const ease = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eout = k => 1 - Math.pow(1 - k, 3);
const back = k => { const c = 1.7; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
const ap = (t, t0, d) => clamp((t - t0) / d);                      // 0..1 ramp
const win = (t, a, b, f = .25) => Math.min(ap(t, a, f), 1 - ap(t, b - f, f));   // fade in at a, out at b

// ---------- camera ----------
let CAM = { lon: 0, lat: 0, ppd: 10 };
function camAt(keys, t) {           // keys: [t, lon, lat, ppd, (easing 'e'|'l'|'o')]
  if (t <= keys[0][0]) return { lon: keys[0][1], lat: keys[0][2], ppd: keys[0][3] };
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1];
    if (t >= a[0] && t < b[0]) {
      let k = (t - a[0]) / Math.max(1e-6, b[0] - a[0]);
      k = (b[4] || 'e') === 'l' ? k : (b[4] === 'o' ? eout(k) : ease(k));
      return { lon: lerp(a[1], b[1], k), lat: lerp(a[2], b[2], k), ppd: Math.exp(lerp(Math.log(a[3]), Math.log(b[3]), k)) };
    }
  }
  const z = keys[keys.length - 1]; return { lon: z[1], lat: z[2], ppd: z[3] };
}
const KX = () => Math.cos(CAM.lat * Math.PI / 180);
function P(lon, lat) { return [W / 2 + (lon - CAM.lon) * CAM.ppd * KX(), H / 2 - (lat - CAM.lat) * CAM.ppd]; }

// ---------- textures ----------
const TEX = [];   // {k, l0, l1, b0, b1, minppd}
function drawTex(T) {
  const im = IM[T.k]; if (!im) return;
  const [x0, y0] = P(T.l0, T.b1), [x1, y1] = P(T.l1, T.b0);
  const sx0 = Math.max(0, x0), sy0 = Math.max(0, y0), sx1 = Math.min(W, x1), sy1 = Math.min(H, y1);
  if (sx1 <= sx0 || sy1 <= sy0) return;
  const fx = im.width / (x1 - x0), fy = im.height / (y1 - y0);
  ctx.drawImage(im, (sx0 - x0) * fx, (sy0 - y0) * fy, (sx1 - sx0) * fx, (sy1 - sy0) * fy, sx0, sy0, sx1 - sx0, sy1 - sy0);
}
function drawMap(dark = 0) {
  ctx.fillStyle = '#183a4e'; ctx.fillRect(0, 0, W, H);
  for (const T of TEX) if (CAM.ppd >= (T.minppd || 0)) drawTex(T);
  if (dark > 0) { ctx.fillStyle = `rgba(4,10,20,${dark})`; ctx.fillRect(0, 0, W, H); }
}
function vignette(a = .5) {
  let g = ctx.createLinearGradient(0, 0, 0, H * .2); g.addColorStop(0, `rgba(0,0,0,${a})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H * .2);
  g = ctx.createLinearGradient(0, H * .8, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`);
  ctx.fillStyle = g; ctx.fillRect(0, H * .8, W, H * .2);
}

// ---------- vector overlays ----------
function pathRings(rings) { ctx.beginPath(); for (const r of rings) { r.forEach((c, i) => { const [x, y] = P(c[0], c[1]); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.closePath(); } }
function glowFill(rings, col, a = 1, o = {}) {      // neon region: tinted fill, glowing edge, thin light inner line
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; pathRings(rings);
  ctx.fillStyle = col; ctx.globalAlpha = a * (o.fill ?? .62); ctx.fill('evenodd');
  ctx.globalAlpha = a; ctx.shadowColor = col; ctx.shadowBlur = o.blur ?? 26; ctx.strokeStyle = col; ctx.lineWidth = o.lw ?? 5; ctx.lineJoin = 'round'; ctx.stroke();
  ctx.shadowBlur = 0; ctx.strokeStyle = 'rgba(255,255,255,.75)'; ctx.lineWidth = 1.6; ctx.stroke();
  ctx.restore();
}
function polyPartial(pts, p, o = {}) {   // stroke a lon/lat polyline up to fraction p of its screen length
  if (p <= 0 || pts.length < 2) return;
  const S = pts.map(c => P(c[0], c[1])); let L = 0; const d = [0];
  for (let i = 1; i < S.length; i++) { L += Math.hypot(S[i][0] - S[i - 1][0], S[i][1] - S[i - 1][1]); d.push(L); }
  const lim = L * clamp(p); ctx.beginPath(); ctx.moveTo(S[0][0], S[0][1]);
  for (let i = 1; i < S.length; i++) {
    if (d[i] <= lim) ctx.lineTo(S[i][0], S[i][1]);
    else { const k = (lim - d[i - 1]) / (d[i] - d[i - 1] || 1); ctx.lineTo(lerp(S[i - 1][0], S[i][0], k), lerp(S[i - 1][1], S[i][1], k)); break; }
  }
  ctx.save(); ctx.strokeStyle = o.col || '#fff'; ctx.lineWidth = o.lw || 5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.shadowColor = o.glow || 'rgba(255,255,255,.8)'; ctx.shadowBlur = o.blur ?? 12; ctx.globalAlpha = o.a ?? 1; ctx.stroke(); ctx.restore();
}

// ---------- text ----------
function txt(s, x, y, size, col = '#fff', font = 'MB', o = {}) {
  ctx.save(); ctx.font = `${size}px ${font}`; ctx.textAlign = o.align || 'center'; ctx.textBaseline = 'middle';
  if (o.ls) ctx.letterSpacing = o.ls + 'px';
  if (o.stroke) { ctx.lineWidth = o.stroke; ctx.strokeStyle = o.sc || 'rgba(0,0,0,.85)'; ctx.lineJoin = 'round'; ctx.strokeText(s, x, y); }
  ctx.shadowColor = o.shadow || 'rgba(0,0,0,.65)'; ctx.shadowBlur = o.blur ?? 14; ctx.shadowOffsetY = o.dy ?? 3;
  ctx.fillStyle = col; ctx.fillText(s, x, y); ctx.restore();
}
function tw(s, size, font = 'MB') { ctx.save(); ctx.font = `${size}px ${font}`; const w = ctx.measureText(s).width; ctx.restore(); return w; }
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function pill(s, x, y, size, a = 1, o = {}) {   // navy rounded plate with text (brand)
  if (a <= 0) return;
  const w = tw(s, size, o.font || 'MX') + size * 1.1, h = size * 1.75;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); const sc = o.scale ?? 1; ctx.scale(sc, sc);
  rr(-w / 2, -h / 2, w, h, h * .32); ctx.fillStyle = o.bg || 'rgba(19,11,84,.86)'; ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 18; ctx.fill();
  ctx.shadowBlur = 0; ctx.strokeStyle = o.line || 'rgba(254,179,0,.45)'; ctx.lineWidth = 2.5; ctx.stroke();
  txt(s, 0, 2, size, o.col || '#fff', o.font || 'MX', { blur: 0, dy: 0 }); ctx.restore();
}
function dot(lon, lat, a = 1, col = BR.acc) {
  if (a <= 0) return; const [x, y] = P(lon, lat);
  ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.arc(x, y, 11, 0, 7); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 18; ctx.fill();
  ctx.lineWidth = 3; ctx.strokeStyle = '#fff'; ctx.stroke(); ctx.restore();
}
function logo(a = .8) {
  const im = IM.logo; if (!im) return; const h = 72, w = im.width / im.height * h;
  ctx.save(); ctx.globalAlpha = a; ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 10; ctx.drawImage(im, W - 48 - w, 48, w, h); ctx.restore();
}
function arrow(x0, y0, x1, y1, cx, cy, p, a = 1, lw = 9) {   // curved white arrow (quadratic), drawn on with p
  if (p <= 0 || a <= 0) return;
  const N = 30, pts = []; for (let i = 0; i <= N * p; i++) { const k = i / N; pts.push([(1 - k) * (1 - k) * x0 + 2 * (1 - k) * k * cx + k * k * x1, (1 - k) * (1 - k) * y0 + 2 * (1 - k) * k * cy + k * k * y1]); }
  if (pts.length < 2) return;
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = '#fff'; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.shadowColor = 'rgba(0,0,0,.6)'; ctx.shadowBlur = 10;
  ctx.beginPath(); pts.forEach((q, i) => i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1])); ctx.stroke();
  const [ex, ey] = pts[pts.length - 1], [px, py] = pts[Math.max(0, pts.length - 3)]; const an = Math.atan2(ey - py, ex - px);
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(ex + Math.cos(an) * 22, ey + Math.sin(an) * 22);
  ctx.lineTo(ex + Math.cos(an + 2.4) * 26, ey + Math.sin(an + 2.4) * 26); ctx.lineTo(ex + Math.cos(an - 2.4) * 26, ey + Math.sin(an - 2.4) * 26); ctx.fill(); ctx.restore();
}

// ---------- CTA + end card (JAS brand) ----------
function cta(t, c) {   // c: {t0 (ЕНТ line), tk (keyword), tl (link line), end, kw}
  const a = ap(t, c.t0, .4); if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a * .55; ctx.fillStyle = '#030814'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const y0 = H * .3;
  const p1 = eout(ap(t, c.t0, .5));
  ctx.save(); ctx.globalAlpha = p1; ctx.translate(0, (1 - p1) * 40);
  txt('Такие вопросы часто', W / 2, y0, 62, '#fff', 'MX'); txt('попадаются на', W / 2, y0 + 82, 62, '#fff', 'MX');
  txt('ЕНТ по географии', W / 2, y0 + 172, 84, BR.acc, 'MB'); ctx.restore();
  const p2 = ap(t, c.tk - .9, .45);
  if (p2 > 0) {
    ctx.save(); ctx.globalAlpha = p2; txt('Напиши в комментариях', W / 2, H * .53, 58, '#fff', 'MX'); ctx.restore();
    const pk = back(ap(t, c.tk, .45));
    if (pk > 0) {
      ctx.save(); ctx.translate(W / 2, H * .63); ctx.scale(pk, pk);
      const w = tw(c.kw, 150, 'MB') + 150; rr(-w / 2, -105, w, 210, 56); ctx.fillStyle = BR.acc; ctx.shadowColor = 'rgba(254,179,0,.6)'; ctx.shadowBlur = 40; ctx.fill();
      txt(c.kw, 0, 8, 150, BR.navy, 'MB', { blur: 0, dy: 0 }); ctx.restore();
    }
  }
  const p3 = eout(ap(t, c.tl, .45));
  if (p3 > 0) {
    ctx.save(); ctx.globalAlpha = p3; ctx.translate(0, (1 - p3) * 30);
    txt('Подготовка к ЕНТ — по ссылке', W / 2, H * .76, 50, '#fff', 'MX'); txt('в шапке профиля или в описании', W / 2, H * .76 + 66, 50, BR.acc, 'MX'); ctx.restore();
  }
}
function endCard(t, t0, kw) {
  const a = ap(t, t0, .45); if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = BR.navy; ctx.fillRect(0, 0, W, H);
  const im = IM.logo, s = .92 + .08 * eout(ap(t, t0, 1.2));
  if (im) { const h = 400 * s, w = im.width / im.height * h; ctx.drawImage(im, W / 2 - w / 2, H * .4 - h / 2, w, h); }
  txt('Пиши в комментариях', W / 2, H * .62, 56, '#fff', 'MX', { blur: 0 });
  txt(`«${kw}»`, W / 2, H * .62 + 110, 120, BR.acc, 'MB', { blur: 0 });
  ctx.restore();
}
