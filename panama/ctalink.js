// CTA without ЕНТ: «Хочешь больше таких фактов? Переходи по ссылке в шапке профиля!» + JAS end card. Needs V('cta'), V('link').
function ctaLink(t) {
  const t0 = V('cta'), a = ap(t, t0, .4); if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a * .66; ctx.fillStyle = '#030814'; ctx.fillRect(0, 0, W, H); ctx.restore();
  const p1 = eout(ap(t, t0, .5));
  ctx.save(); ctx.globalAlpha = p1; ctx.translate(0, (1 - p1) * 40);
  txt('Хочешь больше', W / 2, H * .3, 78, '#fff', 'MB'); txt('таких фактов?', W / 2, H * .3 + 100, 78, BR.acc, 'MB'); ctx.restore();
  const p2 = ap(t, V('link') - .1, .45);
  if (p2 > 0) {
    ctx.save(); ctx.globalAlpha = p2; txt('Переходи по ссылке', W / 2, H * .56, 60, '#fff', 'MX'); ctx.restore();
    const pk = back(ap(t, V('link') + .4, .45));
    if (pk > 0) { ctx.save(); ctx.translate(W / 2, H * .65); ctx.scale(pk, pk); const s = 'в шапке профиля', w = tw(s, 74, 'MB') + 110;
      rr(-w / 2, -70, w, 140, 44); ctx.fillStyle = BR.acc; ctx.shadowColor = 'rgba(254,179,0,.6)'; ctx.shadowBlur = 40; ctx.fill(); txt(s, 0, 5, 74, BR.navy, 'MB', { blur: 0, dy: 0 }); ctx.restore();
      const bob = Math.sin(t * 6) * 12; ctx.save(); ctx.globalAlpha = clamp(pk); ctx.translate(W / 2, H * .145 + bob); ctx.fillStyle = BR.acc; ctx.shadowColor = BR.acc; ctx.shadowBlur = 20;
      ctx.beginPath(); ctx.moveTo(0, -55); ctx.lineTo(46, 0); ctx.lineTo(16, 0); ctx.lineTo(16, 46); ctx.lineTo(-16, 46); ctx.lineTo(-16, 0); ctx.lineTo(-46, 0); ctx.closePath(); ctx.fill(); ctx.restore(); }
  }
}
function endCardLink(t, t0) {
  const a = ap(t, t0, .45); if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = BR.navy; ctx.fillRect(0, 0, W, H);
  const im = IM.logo, s = .92 + .08 * eout(ap(t, t0, 1.2));
  if (im) { const h = 420 * s, w = im.width / im.height * h; ctx.drawImage(im, W / 2 - w / 2, H * .4 - h / 2, w, h); }
  txt('Больше фактов —', W / 2, H * .62, 60, '#fff', 'MX', { blur: 0 }); txt('ссылка в шапке профиля', W / 2, H * .62 + 92, 66, BR.acc, 'MB', { blur: 0 });
  ctx.restore();
}
// sun icon (disc + rays or half-sun over waves)
function sunIcon(x, y, r, a, kind = 'rise') {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y);
  const col = kind === 'rise' ? '#FFC93C' : '#FF7A3D';
  ctx.save(); ctx.beginPath(); ctx.rect(-r * 2, -r * 2, r * 4, r * 2); ctx.clip();
  ctx.beginPath(); ctx.arc(0, 0, r, 0, 7); ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 30; ctx.fill(); ctx.restore();
  ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineWidth = r * .14;
  if (kind === 'rise') for (let i = 0; i < 7; i++) { const an = Math.PI + i * Math.PI / 6; ctx.beginPath(); ctx.moveTo(Math.cos(an) * r * 1.3, Math.sin(an) * r * 1.3); ctx.lineTo(Math.cos(an) * r * 1.7, Math.sin(an) * r * 1.7); ctx.stroke(); }
  ctx.strokeStyle = kind === 'rise' ? '#5EC8E5' : '#FF9B6B'; ctx.lineWidth = r * .16;
  for (let k = 0; k < 3; k++) { ctx.beginPath(); const yy = r * .3 + k * r * .38, ww = r * (1.5 - k * .3); for (let i = 0; i <= 20; i++) { const xx = -ww + 2 * ww * i / 20; const y2 = yy + Math.sin(i / 20 * Math.PI * 4) * r * .06; i ? ctx.lineTo(xx, y2) : ctx.moveTo(xx, y2); } ctx.stroke(); }
  ctx.restore();
}
