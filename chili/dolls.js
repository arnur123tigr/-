// Chibi peg-doll characters, painted beach and ship: reused from the Louisiana reel (louisiana/scene.html), adapted.
const rnd = seed => { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; };
const shade = (hex, f) => { const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255; const m = v => Math.round(clamp(f > 0 ? v + (255 - v) * f : v * (1 + f), 0, 255)); return `rgb(${m(r)},${m(g)},${m(b)})`; };
const DP = {
  conq: { coat: '#9aa3ad', collar: '#b81d24', vest: '#cfd5db', hat: 'morion', hair: '#3a2416', plume: '#c4161f', arm: 'point' },
  conq2: { coat: '#8d96a1', vest: '#c9cfd6', hat: 'morion', hair: '#2a1a10', arm: 'musket' },
  monk: { coat: '#5a3d26', vest: null, hair: '#3a2a1a', plain: true },
  nat: { coat: '#b5562c', vest: null, skin: '#b7835c', hair: '#141010', plain: true, hat: 'band', band: '#e0b84a', feather: '#2a7fb8' },
  nat2: { coat: '#6f8f3a', vest: null, skin: '#a8734e', hair: '#141010', plain: true, hat: 'band', band: '#c4161f' },
  nap: { coat: '#1f2c55', collar: '#b81d24', vest: '#f2eee6', hat: 'bicorne', hair: '#2a1d14', epa: true },
  liv: { coat: '#262626', vest: '#efe9dd', hair: 'wig' },
  mon: { coat: '#3a2a22', vest: '#efe9dd', hair: '#5a3a24' },
  jef: { coat: '#5b3a26', vest: '#d9c9a5', hair: 'wigred' },
  brit: { coat: '#b3202a', collar: '#1e2a55', vest: '#f2eee6', hair: 'wig', epa: true },
  sol: { coat: '#24408f', collar: '#c22', vest: '#f2eee6', hat: 'shako', belts: true },
  slave: { coat: '#c9b48f', vest: null, skin: '#6b4430', hair: '#1a120c', plain: true },
};
function doll(x, y, s, o, ex = {}) {
  o = Object.assign({}, o, ex);
  const skin = o.skin || '#f4dcc8';
  ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); if (o.rot) ctx.rotate(o.rot); if (o.flip) ctx.scale(-1, 1);
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  ctx.fillStyle = 'rgba(0,0,0,.28)'; ctx.beginPath(); ctx.ellipse(0, 0, 30, 6, 0, 0, 7); ctx.fill();
  const arm = (sx, sy, ex2, ey, hand = true) => { ctx.strokeStyle = shade(o.coat, -.15); ctx.lineWidth = 11; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex2, ey); ctx.stroke(); if (hand) { ctx.fillStyle = o.glove ? '#fff' : skin; ctx.beginPath(); ctx.arc(ex2, ey, 6.5, 0, 7); ctx.fill(); } };
  // back arm layer
  if (o.arm === 'shrug') arm(-18, -38, -34, -50);
  // body
  const g = ctx.createLinearGradient(-24, 0, 24, 0); g.addColorStop(0, shade(o.coat, .18)); g.addColorStop(.55, o.coat); g.addColorStop(1, shade(o.coat, -.35));
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-23, -2); ctx.lineTo(-23, -34); ctx.quadraticCurveTo(-23, -47, -10, -48); ctx.lineTo(10, -48); ctx.quadraticCurveTo(23, -47, 23, -34); ctx.lineTo(23, -2); ctx.quadraticCurveTo(0, 3, -23, -2); ctx.fill();
  if (o.vest) { ctx.fillStyle = o.vest; ctx.beginPath(); ctx.moveTo(-9, -48); ctx.lineTo(9, -48); ctx.lineTo(5, -14); ctx.lineTo(-5, -14); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(-7, -48); ctx.lineTo(7, -48); ctx.lineTo(0, -38); ctx.fill(); }
  if (o.collar) { ctx.fillStyle = o.collar; ctx.beginPath(); ctx.moveTo(-14, -47); ctx.lineTo(-8, -47); ctx.lineTo(-4, -30); ctx.lineTo(-11, -34); ctx.fill(); ctx.beginPath(); ctx.moveTo(14, -47); ctx.lineTo(8, -47); ctx.lineTo(4, -30); ctx.lineTo(11, -34); ctx.fill(); }
  if (!o.plain) { ctx.fillStyle = '#d8b04a'; for (const yy of [-36, -28, -20]) { ctx.beginPath(); ctx.arc(-11, yy, 1.8, 0, 7); ctx.arc(11, yy, 1.8, 0, 7); ctx.fill(); } }
  if (o.plain) { ctx.strokeStyle = 'rgba(80,60,40,.5)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(-6, -46); ctx.lineTo(0, -38); ctx.lineTo(6, -46); ctx.stroke(); ctx.fillStyle = '#6b5236'; ctx.fillRect(-23, -18, 46, 5); }
  if (o.belts) { ctx.strokeStyle = '#f4f1ea'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-19, -44); ctx.lineTo(17, -8); ctx.moveTo(19, -44); ctx.lineTo(-17, -8); ctx.stroke(); }
  if (o.epa) { ctx.fillStyle = '#e0b84a'; ctx.beginPath(); ctx.ellipse(-19, -45, 8, 4, -.3, 0, 7); ctx.ellipse(19, -45, 8, 4, .3, 0, 7); ctx.fill(); }
  // front arms
  if (o.arm === 'shake') arm(18, -36, 40, -34);
  if (o.arm === 'point') arm(18, -38, 42, -50);
  if (o.arm === 'fist' || o.arm === 'torch') { arm(18, -40, 30, -78); if (o.arm === 'torch') { ctx.strokeStyle = '#6b4a2a'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(30, -70); ctx.lineTo(32, -100); ctx.stroke(); const fl = 1 + .15 * Math.sin((o.tt || 0) * 25); ctx.fillStyle = '#ffb22a'; ctx.shadowColor = '#ff7a00'; ctx.shadowBlur = 25; ctx.beginPath(); ctx.ellipse(32, -108, 6 * fl, 11 * fl, 0, 0, 7); ctx.fill(); ctx.fillStyle = '#fff3a0'; ctx.beginPath(); ctx.ellipse(32, -105, 3, 6, 0, 0, 7); ctx.fill(); ctx.shadowBlur = 0; } }
  if (o.arm === 'shrug') arm(18, -38, 34, -50);
  if (o.arm === 'musket') { ctx.strokeStyle = '#5a3a1e'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-26, -6); ctx.lineTo(30, -62); ctx.stroke(); ctx.strokeStyle = '#999'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(30, -62); ctx.lineTo(38, -74); ctx.stroke(); arm(-14, -38, 4, -28); }
  if (o.arm === 'case') { arm(18, -36, 30, -20); ctx.fillStyle = '#c9ccd1'; ctx.strokeStyle = '#8a8e96'; ctx.lineWidth = 2; ctx.beginPath(); ctx.roundRect(20, -22, 36, 26, 3); ctx.fill(); ctx.stroke(); ctx.beginPath(); ctx.moveTo(32, -22); ctx.lineTo(32, -27); ctx.lineTo(44, -27); ctx.lineTo(44, -22); ctx.stroke(); }
  // head
  const hy = -70, hr = 26;
  if (o.hair === 'wig' || o.hair === 'wigred') { ctx.fillStyle = o.hair === 'wig' ? '#e9e6e0' : '#c9a48a'; ctx.beginPath(); ctx.arc(-24, hy + 6, 9, 0, 7); ctx.arc(24, hy + 6, 9, 0, 7); ctx.fill(); }
  const hg = ctx.createRadialGradient(-9, hy - 10, 4, 0, hy, hr * 1.1); hg.addColorStop(0, shade(skin, .25)); hg.addColorStop(.7, skin); hg.addColorStop(1, shade(skin, -.2));
  ctx.fillStyle = o.sick ? '#c9d48a' : hg; ctx.beginPath(); ctx.arc(0, hy, hr, 0, 7); ctx.fill();
  if (o.hair && o.hair !== 'none') {
    ctx.fillStyle = o.hair === 'wig' ? '#efece6' : o.hair === 'wigred' ? '#d2ae94' : o.hair;
    ctx.beginPath(); ctx.arc(0, hy - 2, hr + 1, Math.PI * 1.05, Math.PI * 1.95); ctx.quadraticCurveTo(10, hy - 14, 0, hy - 16); ctx.quadraticCurveTo(-14, hy - 14, -25, hy - 6); ctx.fill();
  }
  // face
  const lk = o.look || 0, fe = o.face || 'n';
  ctx.fillStyle = '#1b1410';
  if (fe === 'x') { ctx.strokeStyle = '#1b1410'; ctx.lineWidth = 2.2; for (const ex2 of [-9, 9]) { ctx.beginPath(); ctx.moveTo(ex2 + lk - 3, hy - 3); ctx.lineTo(ex2 + lk + 3, hy + 3); ctx.moveTo(ex2 + lk + 3, hy - 3); ctx.lineTo(ex2 + lk - 3, hy + 3); ctx.stroke(); } }
  else { const eh = fe === 'shock' ? 4.2 : 3.3; ctx.beginPath(); ctx.ellipse(-9 + lk, hy, 2.4, eh, 0, 0, 7); ctx.ellipse(9 + lk, hy, 2.4, eh, 0, 0, 7); ctx.fill(); }
  ctx.strokeStyle = '#1b1410'; ctx.lineWidth = 1.8; ctx.lineCap = 'round'; ctx.beginPath();
  if (fe === 'smile') { ctx.arc(lk, hy + 7, 5, .2, Math.PI - .2); }
  else if (fe === 'shock') { ctx.stroke(); ctx.fillStyle = '#5a2020'; ctx.beginPath(); ctx.ellipse(lk, hy + 11, 3.5, 5, 0, 0, 7); ctx.fill(); ctx.beginPath(); ctx.moveTo(-13 + lk, hy - 9); ctx.lineTo(-6 + lk, hy - 10); ctx.moveTo(6 + lk, hy - 10); ctx.lineTo(13 + lk, hy - 9); }
  else if (fe === 'angry') { ctx.moveTo(-4 + lk, hy + 11); ctx.lineTo(4 + lk, hy + 11); ctx.moveTo(-13 + lk, hy - 8); ctx.lineTo(-5 + lk, hy - 5); ctx.moveTo(13 + lk, hy - 8); ctx.lineTo(5 + lk, hy - 5); }
  else if (fe === 'sad' || fe === 'x') { ctx.arc(lk, hy + 13, 4, Math.PI + .3, -.3); }
  else { ctx.moveTo(-3 + lk, hy + 9); ctx.lineTo(3 + lk, hy + 9); }
  ctx.stroke();
  ctx.fillStyle = 'rgba(230,120,110,.25)'; ctx.beginPath(); ctx.arc(-15 + lk, hy + 6, 4, 0, 7); ctx.arc(15 + lk, hy + 6, 4, 0, 7); ctx.fill();
  if (o.sweat) { ctx.fillStyle = '#9fd4ff'; ctx.beginPath(); ctx.ellipse(22, hy - 10, 3, 5, 0, 0, 7); ctx.fill(); }
  // hats
  if (o.hat === 'morion') {
    const mg = ctx.createLinearGradient(-30, hy - 50, 30, hy - 10); mg.addColorStop(0, '#f2f4f7'); mg.addColorStop(.5, '#b9c0c9'); mg.addColorStop(1, '#6d747e');
    ctx.fillStyle = mg; ctx.beginPath(); ctx.moveTo(-42, hy - 10); ctx.quadraticCurveTo(-36, hy - 22, -24, hy - 22); ctx.quadraticCurveTo(-26, hy - 52, 0, hy - 58); ctx.quadraticCurveTo(26, hy - 52, 24, hy - 22);
    ctx.quadraticCurveTo(36, hy - 22, 42, hy - 10); ctx.quadraticCurveTo(0, hy - 20, -42, hy - 10); ctx.fill(); ctx.strokeStyle = '#59606a'; ctx.lineWidth = 2; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-6, hy - 57); ctx.quadraticCurveTo(0, hy - 72, 6, hy - 57); ctx.fill(); ctx.stroke();
    if (o.plume) { ctx.fillStyle = o.plume; ctx.beginPath(); ctx.ellipse(10, hy - 66, 5, 14, .5, 0, 7); ctx.fill(); }
  }
  if (o.hat === 'band') {
    ctx.fillStyle = o.band || '#c4161f'; ctx.fillRect(-26, hy - 16, 52, 7);
    if (o.feather) { ctx.fillStyle = o.feather; ctx.beginPath(); ctx.ellipse(16, hy - 34, 5, 16, .35, 0, 7); ctx.fill(); ctx.strokeStyle = 'rgba(0,0,0,.35)'; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.moveTo(12, hy - 22); ctx.lineTo(20, hy - 46); ctx.stroke(); }
  }
  if (o.hat === 'bicorne') {
    const bg = ctx.createLinearGradient(0, hy - 46, 0, hy - 14); bg.addColorStop(0, '#2a2a2e'); bg.addColorStop(1, '#0d0d10');
    ctx.fillStyle = bg; ctx.beginPath(); ctx.moveTo(-40, hy - 12); ctx.quadraticCurveTo(-30, hy - 50, 0, hy - 50); ctx.quadraticCurveTo(30, hy - 50, 40, hy - 12); ctx.quadraticCurveTo(0, hy - 24, -40, hy - 12); ctx.fill();
    ctx.strokeStyle = '#d9b24e'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(-40, hy - 12); ctx.quadraticCurveTo(0, hy - 24, 40, hy - 12); ctx.stroke();
    for (const [r, c] of [[7, '#2547a8'], [4.6, '#fff'], [2.4, '#c4161f']]) { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(-18, hy - 26, r, 0, 7); ctx.fill(); }
  }
  if (o.hat === 'shako') {
    ctx.fillStyle = '#141418'; ctx.beginPath(); ctx.moveTo(-20, hy - 16); ctx.lineTo(-17, hy - 52); ctx.lineTo(17, hy - 52); ctx.lineTo(20, hy - 16); ctx.closePath(); ctx.fill();
    ctx.fillStyle = '#0b0b0d'; ctx.beginPath(); ctx.ellipse(0, hy - 15, 23, 5, 0, 0, 7); ctx.fill();
    ctx.fillStyle = '#d9b24e'; ctx.beginPath(); ctx.moveTo(0, hy - 42); ctx.lineTo(8, hy - 32); ctx.lineTo(0, hy - 22); ctx.lineTo(-8, hy - 32); ctx.fill();
    ctx.fillStyle = '#d8232e'; ctx.beginPath(); ctx.ellipse(0, hy - 62, 6, 11, 0, 0, 7); ctx.fill(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(0, hy - 52, 4, 0, 7); ctx.fill();
  }
  if (o.chain) { ctx.strokeStyle = '#333'; ctx.lineWidth = 2.5; for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.ellipse(-18 - i * 6, -2 + i * .8, 3.5, 2.2, 0, 0, 7); ctx.stroke(); } ctx.fillStyle = '#222'; ctx.beginPath(); ctx.arc(-58, 0, 10, 0, 7); ctx.fill(); ctx.fillStyle = 'rgba(255,255,255,.25)'; ctx.beginPath(); ctx.arc(-61, -3, 3, 0, 7); ctx.fill(); }
  ctx.restore();
}

function flagES(w = 60) { const h = w * .66; ctx.strokeStyle = '#5a3a1e'; ctx.lineWidth = w * .06; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -h * 2.1); ctx.stroke();
  ctx.fillStyle = '#f4efe0'; ctx.fillRect(0, -h * 2.1, w, h); ctx.strokeStyle = '#c4161f'; ctx.lineWidth = w * .1; ctx.beginPath(); ctx.moveTo(w * .15, -h * 2.0); ctx.lineTo(w * .85, -h * 1.2); ctx.moveTo(w * .85, -h * 2.0); ctx.lineTo(w * .15, -h * 1.2); ctx.stroke(); }
function flagPT(w = 60) { const h = w * .66; ctx.strokeStyle = '#5a3a1e'; ctx.lineWidth = w * .06; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -h * 2.1); ctx.stroke();
  ctx.fillStyle = '#f4efe0'; ctx.fillRect(0, -h * 2.1, w, h); ctx.fillStyle = '#1f3c9a'; ctx.beginPath(); ctx.arc(w / 2, -h * 1.6, h * .3, 0, 7); ctx.fill(); }
function flagFR(w = 60) { const h = w * .66; ctx.strokeStyle = '#5a3a1e'; ctx.lineWidth = w * .06; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -h * 2.1); ctx.stroke();
  [['#24409f', 0], ['#fff', 1], ['#d0202a', 2]].forEach(([c, i]) => { ctx.fillStyle = c; ctx.fillRect(i * w / 3, -h * 2.1, w / 3 + .5, h); }); }
function flagUS(w = 60) { const h = w * .62; ctx.strokeStyle = '#5a3a1e'; ctx.lineWidth = w * .06; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -h * 2.1); ctx.stroke();
  for (let i = 0; i < 7; i++) { ctx.fillStyle = i % 2 ? '#fff' : '#c4161f'; ctx.fillRect(0, -h * 2.1 + i * h / 7, w, h / 7 + .5); } ctx.fillStyle = '#1f2e72'; ctx.fillRect(0, -h * 2.1, w * .42, h * .55); }
function ship(sz = 1, flag = 'us', crew = 2, tt = 0) {
  ctx.save(); ctx.scale(sz, sz); ctx.rotate(Math.sin(tt * 3) * .05);
  if (crew) { if (crew >= 1) doll(-12, -10, 50, DP.conq2); if (crew >= 2) doll(14, -10, 50, DP.conq); }
  ctx.fillStyle = '#7a4a26'; ctx.beginPath(); ctx.moveTo(-60, -22); ctx.lineTo(62, -22); ctx.lineTo(48, 6); ctx.lineTo(-48, 6); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#9c6234'; ctx.fillRect(-58, -22, 118, 7); ctx.fillStyle = '#4a2c14'; for (let i = -40; i <= 40; i += 20) { ctx.beginPath(); ctx.arc(i, -8, 3, 0, 7); ctx.fill(); }
  ctx.strokeStyle = '#5a3a1e'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(34, -22); ctx.lineTo(34, -110); ctx.stroke();
  ctx.fillStyle = '#f2ece0'; ctx.beginPath(); ctx.moveTo(36, -104); ctx.quadraticCurveTo(70, -76, 38, -36); ctx.closePath(); ctx.fill();
  ctx.save(); ctx.translate(34, -104); ctx.scale(.5, .5); if (flag === 'pt') flagPT(50); else flagES(50); ctx.restore();
  ctx.restore();
}
function paintSky(g, hz) { const s = g.createLinearGradient(0, 0, 0, hz); s.addColorStop(0, '#5f9fdc'); s.addColorStop(.7, '#a9cdee'); s.addColorStop(1, '#e6eef2'); g.fillStyle = s; g.fillRect(0, 0, W, hz + 5);
  const r = rnd(11); for (let i = 0; i < 9; i++) { const x = r() * W, y = 80 + r() * hz * .55, w = 160 + r() * 260; g.save(); g.translate(x, y); g.filter = 'blur(6px)'; g.fillStyle = 'rgba(255,255,255,.9)'; for (let k = 0; k < 6; k++) { g.beginPath(); g.ellipse((k - 2.5) * w * .18, -Math.sin(k / 5 * Math.PI) * w * .12, w * .2, w * .13, 0, 0, 7); g.fill(); } g.fillStyle = 'rgba(200,215,230,.6)'; g.beginPath(); g.ellipse(0, w * .05, w * .5, w * .07, 0, 0, 7); g.fill(); g.restore(); }
}
function paintMountains(g, hz, col) { const r = rnd(5); g.fillStyle = col; g.beginPath(); g.moveTo(0, hz); for (let x = 0; x <= W; x += 30) g.lineTo(x, hz - 60 - 90 * Math.abs(Math.sin(x / 260 + 1)) - r() * 18); g.lineTo(W, hz); g.fill(); }
let BG_BEACH;
function makeBGs() {
  let g; const r = rnd(9);
  // beach: sky, mountains, sea, sand, palms
  BG_BEACH = document.createElement('canvas'); BG_BEACH.width = W; BG_BEACH.height = H; g = BG_BEACH.getContext('2d'); const bz = 1000;
  paintSky(g, bz); g.filter = 'blur(2px)'; paintMountains(g, bz - 40, '#6f8f8a'); g.filter = 'none';
  g.fillStyle = '#2f5a2a'; for (let x = 0; x < W; x += 16) { g.beginPath(); g.arc(x, bz - 40 + r() * 10, 20 + r() * 10, 0, 7); g.fill(); }
  const sg = g.createLinearGradient(0, bz - 30, 0, bz + 120); sg.addColorStop(0, '#2a8fa8'); sg.addColorStop(1, '#5cc4c8'); g.fillStyle = sg; g.fillRect(0, bz - 30, W, 150);
  const sd = g.createLinearGradient(0, bz + 110, 0, H); sd.addColorStop(0, '#e6d3a6'); sd.addColorStop(1, '#cdb183'); g.fillStyle = sd; g.fillRect(0, bz + 110, W, H);
  for (let i = 0; i < 6000; i++) { g.fillStyle = `rgba(${r() < .5 ? '140,110,70' : '255,245,220'},${.2 + r() * .2})`; g.fillRect(r() * W, bz + 110 + r() * 800, 2, 2); }
  const palm = (x, y, h, lean) => { g.strokeStyle = '#6a5034'; g.lineWidth = h * .05; g.lineCap = 'round'; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + lean * .4, y - h * .6, x + lean, y - h); g.stroke();
    const tx = x + lean, ty = y - h; for (let i = 0; i < 9; i++) { const a = -Math.PI / 2 + (i - 4) * .42; g.strokeStyle = i % 2 ? '#2f6a2a' : '#3f8a34'; g.lineWidth = h * .035; g.beginPath(); g.moveTo(tx, ty); g.quadraticCurveTo(tx + Math.cos(a) * h * .3, ty + Math.sin(a) * h * .3 - h * .06, tx + Math.cos(a) * h * .45, ty + Math.sin(a) * h * .2 + h * .12); g.stroke(); } };
  g.filter = 'blur(1.5px)'; palm(120, 1180, 700, 80); palm(260, 1150, 520, -40); palm(950, 1170, 650, -90); palm(820, 1120, 420, 30); g.filter = 'none';
}

