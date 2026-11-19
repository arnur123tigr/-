// ---------- helpers ----------
function rng(s) { return () => { s = (s * 16807) % 2147483647; return s / 2147483647; }; }
function head(s, a, col, y = H * .17, size = 84) {
  if (a <= 0) return; const p = back(clamp(a * 1.5));
  ctx.save(); ctx.globalAlpha = clamp(a * 2); ctx.translate(W / 2, y); ctx.scale(p, p);
  txt(s, 0, 0, Math.min(size, size * 960 / tw(s, size, 'MB')), '#fff', 'MB', { shadow: col, blur: 26, dy: 0, stroke: 9, sc: 'rgba(0,0,0,.5)' }); ctx.restore();
}
function label2(lines, lon, lat, a, col, size = 64, dy = 0) {
  if (a <= 0) return; const [x, y] = P(lon, lat); const p = back(clamp(a * 1.4));
  ctx.save(); ctx.globalAlpha = clamp(a * 2); ctx.translate(x, y + dy); ctx.scale(p, p);
  lines.forEach((l, i) => txt(l, 0, (i - (lines.length - 1) / 2) * size * 1.08, size, '#fff', 'MB', { shadow: col, blur: 24, dy: 0, stroke: size * .12, sc: 'rgba(0,0,0,.55)' }));
  ctx.restore();
}
function captions(t) {
  const vt = t - OFF; if (vt >= B.cta - .05) return; const c = CAPS.find(c => vt >= c[0] - .05 && vt < c[1] + .05); if (!c) return;
  const a = Math.min(ap(vt, c[0] - .05, .12), 1);
  ctx.save(); ctx.globalAlpha = a; txt(c[2], W / 2, H * .845, 52, '#fff', 'MX', { shadow: 'rgba(0,0,0,.9)', blur: 14, dy: 2, stroke: 7, sc: 'rgba(0,0,0,.5)' }); ctx.restore();
}
function star(x, y, r, a, col = BR.acc) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.beginPath();
  for (let i = 0; i < 10; i++) { const rr_ = i % 2 ? r * .45 : r, an = -Math.PI / 2 + i * Math.PI / 5; ctx.lineTo(Math.cos(an) * rr_, Math.sin(an) * rr_); }
  ctx.closePath(); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 20; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = '#fff'; ctx.stroke(); ctx.restore();
}
function numDisc(n, x, y, a, col) {
  if (a <= 0) return; const s = back(clamp(a)); ctx.save(); ctx.globalAlpha = clamp(a * 2); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.arc(0, 0, 34, 0, 7); ctx.fillStyle = BR.navy; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = col; ctx.stroke();
  txt(String(n), 0, 3, 40, '#fff', 'MB', { blur: 0, dy: 0 }); ctx.restore();
}
function sheikh(x, y, r, a, ring = BR.acc, crown = 0) {   // stylised portrait disc: ghutra + agal
  if (a <= 0) return; ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y);
  ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); const g = ctx.createLinearGradient(0, -r, 0, r); g.addColorStop(0, '#2a2070'); g.addColorStop(1, BR.navy); ctx.fillStyle = g;
  ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 16; ctx.fill(); ctx.shadowBlur = 0; ctx.save(); ctx.clip();
  const k = r / 100;
  ctx.fillStyle = '#f4f4f4'; ctx.beginPath(); ctx.moveTo(-70 * k, 100 * k); ctx.quadraticCurveTo(-62 * k, -10 * k, -40 * k, -48 * k); ctx.quadraticCurveTo(0, -78 * k, 40 * k, -48 * k);
  ctx.quadraticCurveTo(62 * k, -10 * k, 70 * k, 100 * k); ctx.closePath(); ctx.fill();   // ghutra
  ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.ellipse(0, 100 * k, 78 * k, 40 * k, 0, Math.PI, 0); ctx.fill();   // thobe shoulders
  ctx.fillStyle = '#c8956b'; ctx.beginPath(); ctx.ellipse(0, -2 * k, 24 * k, 30 * k, 0, 0, 7); ctx.fill();   // face
  ctx.fillStyle = '#3a2a22'; ctx.beginPath(); ctx.ellipse(0, 18 * k, 20 * k, 14 * k, 0, 0, Math.PI); ctx.fill();   // beard
  ctx.strokeStyle = '#151515'; ctx.lineWidth = 9 * k; ctx.beginPath(); ctx.ellipse(0, -44 * k, 38 * k, 9 * k, 0, 0, 7); ctx.stroke();   // agal
  ctx.restore();
  ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.lineWidth = Math.max(3, r * .08); ctx.strokeStyle = ring; ctx.stroke();
  if (crown > 0) { ctx.save(); ctx.globalAlpha = a * crown; ctx.translate(0, -r - 18 * (r / 60)); const c = r / 60; ctx.scale(c, c);
    ctx.beginPath(); ctx.moveTo(-34, 14); ctx.lineTo(-38, -16); ctx.lineTo(-17, 0); ctx.lineTo(0, -24); ctx.lineTo(17, 0); ctx.lineTo(38, -16); ctx.lineTo(34, 14); ctx.closePath();
    ctx.fillStyle = BR.acc; ctx.shadowColor = BR.acc; ctx.shadowBlur = 18; ctx.fill(); ctx.restore(); }
  ctx.restore();
}
function panel(a, kind = 'grid') {   // navy blueprint background (brand)
  if (a <= 0) return; ctx.save(); ctx.globalAlpha = a;
  const g = ctx.createRadialGradient(W / 2, H * .45, 100, W / 2, H * .45, H * .8); g.addColorStop(0, '#1d2a6e'); g.addColorStop(1, '#0a0730'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(120,150,255,.12)'; ctx.lineWidth = 2; for (let x = 0; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 0; y < H; y += 60) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); } ctx.restore();
}
function shapeAt(o, cx, cy, ppd, col, a, s = 1) {   // centred country outline at true relative size
  if (a <= 0) return; const kx = Math.cos(o.lat * Math.PI / 180) * ppd * s, ky = ppd * s;
  ctx.save(); ctx.globalAlpha = a; ctx.beginPath();
  for (const r of o.r) r.forEach(([x, y], i) => i ? ctx.lineTo(cx + x * kx, cy - y * ky) : ctx.moveTo(cx + x * kx, cy - y * ky));
  ctx.closePath(); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 30; ctx.fill(); ctx.shadowBlur = 0; ctx.lineWidth = 3; ctx.strokeStyle = '#fff'; ctx.stroke(); ctx.restore();
}
function cutFade(t, cuts) { let a = 0; for (const c of cuts) a = Math.max(a, 1 - Math.abs(t - c) / .22); if (a > 0) { ctx.save(); ctx.globalAlpha = clamp(a); ctx.fillStyle = '#05060f'; ctx.fillRect(0, 0, W, H); ctx.restore(); } }

// ---------- CTA + end card ----------
function ctaLink(t) {
  const t0 = V('cta'), a = ap(t, t0, .4); if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a * .62; ctx.fillStyle = '#030814'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const p1 = eout(ap(t, t0, .5));
  ctx.save(); ctx.globalAlpha = p1; ctx.translate(0, (1 - p1) * 40);
  txt('Хочешь больше', W / 2, H * .36, 76, '#fff', 'MB'); txt('таких фактов?', W / 2, H * .36 + 96, 76, BR.acc, 'MB'); ctx.restore();
  const p2 = ap(t, V('link') - .1, .45);
  if (p2 > 0) {
    ctx.save(); ctx.globalAlpha = p2; txt('Переходи по ссылке', W / 2, H * .56, 62, '#fff', 'MX'); ctx.restore();
    const pk = back(ap(t, V('link') + .5, .45));
    if (pk > 0) { ctx.save(); ctx.translate(W / 2, H * .655); ctx.scale(pk, pk); const s = 'в шапке профиля', w = tw(s, 74, 'MB') + 110;
      rr(-w / 2, -70, w, 140, 44); ctx.fillStyle = BR.acc; ctx.shadowColor = 'rgba(254,179,0,.6)'; ctx.shadowBlur = 40; ctx.fill(); txt(s, 0, 5, 74, BR.navy, 'MB', { blur: 0, dy: 0 }); ctx.restore();
      const bob = Math.sin(t * 6) * 14; ctx.save(); ctx.globalAlpha = clamp(pk); ctx.translate(W / 2, H * .29 + bob); ctx.fillStyle = BR.acc; ctx.shadowColor = BR.acc; ctx.shadowBlur = 20;
      ctx.beginPath(); ctx.moveTo(0, -60); ctx.lineTo(50, 0); ctx.lineTo(18, 0); ctx.lineTo(18, 50); ctx.lineTo(-18, 50); ctx.lineTo(-18, 0); ctx.lineTo(-50, 0); ctx.closePath(); ctx.fill(); ctx.restore(); }
  }
}
function endCardLink(t, t0) {
  const a = ap(t, t0, .45); if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = BR.navy; ctx.fillRect(0, 0, W, H);
  const im = IM.logo, s = .92 + .08 * eout(ap(t, t0, 1.2));
  if (im) { const h = 400 * s, w = im.width / im.height * h; ctx.drawImage(im, W / 2 - w / 2, H * .4 - h / 2, w, h); }
  txt('Ссылка', W / 2, H * .62, 64, '#fff', 'MX', { blur: 0 }); txt('в шапке профиля', W / 2, H * .62 + 95, 86, BR.acc, 'MB', { blur: 0 });
  ctx.restore();
}

