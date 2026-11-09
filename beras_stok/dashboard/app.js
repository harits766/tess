// Monitor Stok Beras: semua angka dibaca dari dataset; teks tetap ada di index.html.
d3.formatDefaultLocale({decimal: ',', thousands: '.', grouping: [3], currency: ['Rp', '']});
const BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
const per = (s) => (s && s.length >= 7 ? BLN[+s.slice(5, 7) - 1] + ' ' + s.slice(0, 4) : String(s || ''));
const tgl = (s) => new Date(Date.UTC(+s.slice(0, 4), +s.slice(5, 7) - 1, 1));
const F = {
  0: d3.format(',.0f'), 1: d3.format(',.1f'), 2: d3.format(',.2f'), 3: d3.format(',.3f'),
  s1: d3.format('+,.1f'), s2: d3.format('+,.2f'), pct: d3.format('.0%'), pct1: d3.format('.1%'),
  spct: d3.format('+.1%'), txt: String, per,
};
const KOMP = {total: 'Total', bulog: 'BULOG', swasta: 'Swasta', rumah_tangga: 'Rumah tangga', penggilingan: 'Penggilingan',
  pedagang: 'Pedagang', horeka: 'Horeka'};
const DEF = {periode: '2026-09', komponen: 'total', wil: 'nasional|INDONESIA', bulan: '2026-12'};
const P = () => Object.assign({}, DEF, ...Object.entries(dash.params()).filter(([, v]) => v != null && v !== '').map(([k, v]) => ({[k]: v})));
const warna = (i) => dash.colors[i % dash.colors.length];

const rows = (id) => {
  const g = dash.data(id);
  return g.status === 'ok' && Array.isArray(g.data) ? g.data : null;
};
const status = (ids) => {
  const s = ids.map((i) => dash.data(i).status);
  if (s.some((x) => x === 'error' || x === 'missing' || x === 'declined' || x === 'connect')) return 'error';
  return s.every((x) => x === 'ok') ? 'ok' : 'loading';
};
let srcS = null;
let idxS = null;
const stokIdx = () => {
  const r = rows('stok');
  if (!r) return null;
  if (r !== srcS) {
    srcS = r;
    idxS = new Map(r.map((x) => [x.id, x]));
  }
  return idxS;
};
const seri = (tk, w, k) => (rows('stok') || [])
  .filter((x) => x.tingkat === tk && x.wilayah === w && x.komponen === k)
  .sort((a, b) => d3.ascending(a.periode, b.periode));

// ---------- perhitungan yang terlihat di Sumber ----------
dash.calc('ringkas_nasional', {
  inputs: ['stok'],
  title: 'Perubahan stok nasional',
  description: 'Selisih median stok nasional: Sep 2026 dikurangi Sep 2025, dan prakiraan Des 2026 dikurangi Sep 2026.',
  fn: (stok) => {
    const m = (p, k, f) => (stok.find((r) => r.tingkat === 'nasional' && r.periode === p && r.komponen === k) || {})[f || 'median'];
    return [{
      total_selisih: m('2026-09', 'total') - m('2025-09', 'total'),
      bulog_selisih: m('2026-09', 'bulog') - m('2025-09', 'bulog'),
      swasta_selisih: m('2026-09', 'swasta') - m('2025-09', 'swasta'),
      cukup_selisih: m('2026-09', 'total', 'cukup_bulan') - m('2025-09', 'total', 'cukup_bulan'),
      des_selisih: m('2026-12', 'total') - m('2026-09', 'total'),
      bulog_porsi: m('2026-09', 'bulog') / m('2026-09', 'total'),
      bulog_porsi_lalu: m('2025-09', 'bulog') / m('2025-09', 'total'),
    }];
  },
});
dash.calc('komponen_pulau', {
  inputs: ['stok'],
  title: 'Komponen per pulau',
  description: 'Median tiap komponen stok per pulau dan nasional, satu baris per bulan dan wilayah.',
  fn: (stok) => {
    const out = new Map();
    for (const r of stok) {
      if (r.tingkat === 'provinsi') continue;
      const k = r.periode + '|' + r.wilayah;
      if (!out.has(k)) out.set(k, {periode: r.periode, wilayah: r.wilayah, nama: r.nama, tingkat: r.tingkat});
      out.get(k)[r.komponen] = r.median;
    }
    return [...out.values()];
  },
});
dash.calc('varian_pulau', {
  inputs: ['varian'],
  title: 'Varian INATRADE per pulau',
  description: 'Median stok akhir Sep 2026 per pulau dan nasional untuk tiap varian data INATRADE, dan selisihnya dari dasar.',
  fn: (varian) => {
    const kol = {'Keduanya (dasar)': 'dasar', 'Non PAW saja': 'non_paw', 'PAW saja': 'paw', 'Tanpa INATRADE': 'tanpa_inatrade'};
    const m = new Map();
    for (const r of varian) {
      if (r.periode !== '2026-09') continue;
      if (!m.has(r.wilayah)) m.set(r.wilayah, {wilayah: r.wilayah, tingkat: r.tingkat});
      m.get(r.wilayah)[kol[r.varian]] = r.median;
    }
    return [...m.values()].map((r) => Object.assign(r, {
      non_paw_persen: r.non_paw / r.dasar - 1, paw_persen: r.paw / r.dasar - 1, tanpa_persen: r.tanpa_inatrade / r.dasar - 1,
    }));
  },
});
dash.calc('varian_ringkas', {
  inputs: ['varian'],
  title: 'Varian INATRADE nasional',
  description: 'Stok nasional Sep 2026 per varian, selisih dari dasar, dan rata-rata selisih absolut bulanan Jan 2024–Sep 2026.',
  fn: (varian) => {
    const nas = varian.filter((r) => r.tingkat === 'nasional');
    const dasar = new Map(nas.filter((r) => r.urut === 0).map((r) => [r.periode, r.median]));
    const nama = [...new Set(nas.map((r) => r.varian))];
    return nama.map((v) => {
      const rs = nas.filter((r) => r.varian === v);
      const a = rs.find((r) => r.periode === '2026-09');
      const b = dasar.get('2026-09');
      const abs = rs.map((r) => Math.abs(r.median - dasar.get(r.periode)));
      return {varian: v, median: a.median, p05: a.p05, p95: a.p95, selisih: a.median - b, persen: a.median / b - 1,
        lebar: a.p95 - a.p05, rata_selisih_bulanan: abs.reduce((s, x) => s + x, 0) / abs.length};
    });
  },
});
dash.calc('lebar_interval', {
  inputs: ['stok'],
  title: 'Provinsi paling tidak pasti',
  description: 'Sepuluh provinsi dengan rentang 90% stok total terlebar pada Sep 2026, dan porsinya dari jumlah rentang semua provinsi.',
  fn: (stok) => {
    const p = stok.filter((r) => r.tingkat === 'provinsi' && r.komponen === 'total' && r.periode === '2026-09');
    const jumlah = p.reduce((s, r) => s + (r.p95 - r.p05), 0);
    return p.map((r) => ({id: r.id, nama: r.nama, pulau: r.pulau, median: r.median, lebar: r.p95 - r.p05,
      lebar_relatif: (r.p95 - r.p05) / r.median, porsi_lebar: (r.p95 - r.p05) / jumlah}))
      .sort((a, b) => b.lebar - a.lebar).slice(0, 10);
  },
});
dash.calc('banding', {
  inputs: ['pembanding', 'stok', 'uji'],
  title: 'Pembanding vs model',
  description: 'Angka neraca Bapanas, USDA dan survei di samping median stok nasional model pada bulan yang sama.',
  fn: (pembanding, stok, uji) => pembanding.map((r) => {
    const s = stok.find((x) => x.tingkat === 'nasional' && x.komponen === 'total' && x.periode === r.periode)
      || uji.find((x) => x.jenis === 'validasi' && x.periode === r.periode);
    return {id: r.id, sumber: r.sumber, periode: r.periode, nilai: r.nilai, model: s ? s.median : null,
      rasio: s ? r.nilai / s.median : null, catatan: r.catatan};
  }),
});
dash.calc('turunan', {
  inputs: ['parameter', 'jembatan'],
  title: 'Angka turunan parameter',
  description: 'Rasio survei terhadap level model (eksponen bias log), surplus tahunan dari jembatan, konsumsi per bulan 2026, dan dampak satu poin susut.',
  fn: (parameter, jembatan) => {
    const p = (id) => parameter.find((r) => r.id === id).mean;
    const j = (id) => jembatan.find((r) => r.id === id).nilai;
    const sur = (y) => j(y + '|Produksi setelah susut') + j(y + '|Impor') + j(y + '|Konsumsi');
    return [{
      ssbat_rasio: Math.exp(p('bias_survei[0]')), scbn_rasio: Math.exp(p('bias_survei[1]')),
      inatrade_rasio: Math.exp(p('bias_bulog_inatrade')),
      surplus_2024: sur('2024'), surplus_2025: sur('2025'), surplus_2026: sur('Jan–Sep 2026'),
      neraca_2024: j('2024|Produksi setelah susut') + j('2024|Konsumsi'),
      konsumsi_bulanan_2026: -j('Jan–Sep 2026|Konsumsi') / 9,
      per_poin_susut: j('2025|Produksi setelah susut') / (1 - p('susut') / 100) / 100,
    }];
  },
});

// ---------- angka tunggal ----------
const cari = (el) => {
  const rs = rows(el.dataset.source);
  if (!rs) return undefined;
  if (el.dataset.row != null) return rs[+el.dataset.row];
  const w = (el.dataset.where || '').split('&').filter(Boolean).map((p) => p.split('=').map(decodeURIComponent));
  if (el.dataset.source === 'stok' && w.length === 1 && w[0][0] === 'id') return stokIdx().get(w[0][1]);
  return rs.find((x) => w.every(([k, v]) => String(x[k]) === v));
};
dash.draw('v', (el) => {
  const r = cari(el);
  const v = r ? r[el.dataset.field] : null;
  el.classList.toggle('dash-skeleton', r === undefined && status([el.dataset.source]) === 'loading');
  el.textContent = v == null || (typeof v === 'number' && !isFinite(v)) ? '—' : (F[el.dataset.fmt || '1'] || F[1])(v);
});
dash.draw('delta', (el) => {
  const r = cari(el);
  const v = r ? r[el.dataset.field] : null;
  el.classList.toggle('dash-skeleton', r === undefined && status([el.dataset.source]) === 'loading');
  el.classList.remove('sb-naik', 'sb-turun');
  if (v == null || !isFinite(v)) {
    el.textContent = '—';
    return;
  }
  el.textContent = (F[el.dataset.fmt || 's1'])(v);
  if (Math.abs(v) >= 0.05) el.classList.add(v > 0 ? 'sb-naik' : 'sb-turun');
});
dash.draw('arah', (el) => {
  const r = cari(el);
  const v = r ? r[el.dataset.kolom] : null;
  el.textContent = v == null ? '—' : Math.abs(v) < 0.05 ? 'hampir sama' : v > 0 ? 'naik' : 'turun';
});

// ---------- grafik ----------
const gagal = (el) => {
  const d = document.createElement('div');
  d.className = 'sb-gagal';
  const dot = document.createElement('span');
  dot.className = 'sb-dot';
  const t = document.createElement('span');
  t.textContent = 'Gagal memuat';
  d.append(dot, t);
  el.replaceChildren(d);
};
const grafik = (name, ids, fn) => dash.draw(name, (el) => {
  const s = status(ids);
  el.classList.toggle('dash-skeleton', s === 'loading');
  if (s !== 'ok') {
    el.replaceChildren();
    if (s === 'error') gagal(el);
    return;
  }
  el.replaceChildren();
  fn(el);
});
const ukur = (svg, cls, texts) => {
  const t = svg.append('text').attr('class', cls);
  const w = d3.max(texts, (s) => {
    t.text(s);
    return t.node().getComputedTextLength();
  }) || 0;
  t.remove();
  return w;
};
const tipBaru = (el) => {
  const t = document.createElement('div');
  t.className = 'sb-tip';
  t.hidden = true;
  el.appendChild(t);
  return t;
};
const tipIsi = (tip, judul, baris) => {
  const h = document.createElement('div');
  h.className = 'sb-tip-h';
  h.textContent = judul;
  tip.replaceChildren(h, ...baris.map(([c, nama, nilai]) => {
    const d = document.createElement('div');
    d.className = 'sb-tip-r';
    if (c) {
      const sw = document.createElement('span');
      sw.className = 'sb-sw';
      sw.style.background = c;
      d.appendChild(sw);
    }
    const n = document.createElement('span');
    n.textContent = nama;
    const v = document.createElement('b');
    v.textContent = nilai;
    d.append(n, v);
    return d;
  }));
};
const tipTaruh = (el, tip, x, y) => {
  tip.hidden = false;
  const W = el.clientWidth;
  const w = tip.offsetWidth;
  tip.style.left = Math.max(0, Math.min(W - w, x + 14 > W - w ? x - w - 14 : x + 14)) + 'px';
  tip.style.top = Math.max(0, y - tip.offsetHeight / 2) + 'px';
};

// series: [{name, rows, color, band, dash, kind:'garis'|'titik', f}]
function grafikGaris(el, series, o) {
  o = o || {};
  const W = Math.max(260, el.clientWidth || 600);
  const H = o.h || 300;
  series.forEach((s) => {
    s.d = s.rows.filter((r) => r[s.f || 'median'] != null).map((r) => Object.assign({t: tgl(r.periode), v: r[s.f || 'median']}, r));
  });
  const all = series.flatMap((s) => s.d);
  if (!all.length) return;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`)
    .attr('class', 'sb-svg').attr('role', 'img').attr('aria-label', o.label || '');
  const yMax = d3.max(series, (s) => d3.max(s.d, (r) => (s.band ? r.p95 : r.v)));
  const y = d3.scaleLinear([0, yMax * 1.04], [H - 24, 14]).nice();
  const tf = y.tickFormat(5);
  const ticks = y.ticks(5);
  const ml = ukur(svg, 'sb-tick', ticks.map(tf)) + 10;
  const ujung = series.filter((s) => s.kind !== 'titik' && s.d.length).map((s) => ({s, r: s.d[s.d.length - 1]}));
  ujung.forEach((u) => {
    u.teks = u.s.name + ' ' + F[1](u.r.v);
  });
  const mr = Math.min(W * 0.4, ukur(svg, 'sb-end', ujung.map((u) => u.teks)) + 12);
  const xd = d3.extent(all, (r) => r.t);
  if (o.dari) xd[0] = d3.min([xd[0], tgl(o.dari)]);
  const x = d3.scaleUtc(xd, [ml, W - mr]);
  // prakiraan
  const pr = all.filter((r) => r.jenis === 'prakiraan');
  if (pr.length) {
    const x0 = x(d3.utcDay.offset(d3.min(pr, (r) => r.t), -15));
    svg.append('rect').attr('class', 'sb-zona').attr('x', x0).attr('y', 14).attr('width', Math.max(0, W - mr - x0)).attr('height', H - 38);
    svg.append('text').attr('class', 'sb-tick').attr('x', x0 + 4).attr('y', 26).text('Prakiraan');
  }
  svg.append('g').selectAll('line').data(ticks).join('line').attr('class', 'sb-grid')
    .attr('x1', ml).attr('x2', W - mr).attr('y1', (t) => y(t)).attr('y2', (t) => y(t));
  svg.append('g').selectAll('text').data(ticks).join('text').attr('class', 'sb-tick').attr('text-anchor', 'end')
    .attr('x', ml - 6).attr('y', (t) => y(t) + 4).text(tf);
  const bulan = d3.utcMonth.count(xd[0], xd[1]);
  const lebarTick = (W - ml - mr) / Math.max(1, bulan);
  const step = [1, 3, 6, 12, 24].find((k) => k * lebarTick >= 44) || 24;
  const xt = x.ticks(d3.utcMonth.every(step)).filter((d) => step < 12 || d.getUTCMonth() === 0);
  svg.append('g').selectAll('text').data(xt).join('text').attr('class', 'sb-tick').attr('text-anchor', 'middle')
    .attr('x', (d) => x(d)).attr('y', H - 6)
    .text((d) => (d.getUTCMonth() === 0 || step >= 12 ? String(d.getUTCFullYear()) : BLN[d.getUTCMonth()]));
  svg.append('line').attr('class', 'sb-axis').attr('x1', ml).attr('x2', W - mr).attr('y1', y(0)).attr('y2', y(0));
  series.forEach((s, i) => {
    const c = s.color || warna(i);
    if (s.kind === 'titik') {
      svg.append('g').selectAll('path').data(s.d).join('path')
        .attr('transform', (r) => `translate(${x(r.t)},${y(r.v)})`)
        .attr('d', d3.symbol(s.simbol || d3.symbolCircle, 46)).style('fill', c).style('stroke', 'var(--color-panel)');
      return;
    }
    if (s.band) {
      svg.append('path').datum(s.d).attr('class', 'sb-band').style('fill', c)
        .attr('d', d3.area().x((r) => x(r.t)).y0((r) => y(r.p05)).y1((r) => y(r.p95)));
    }
    const est = s.d.filter((r) => r.jenis !== 'prakiraan');
    const pra = s.d.filter((r) => r.jenis === 'prakiraan');
    const ln = d3.line().x((r) => x(r.t)).y((r) => y(r.v));
    svg.append('path').datum(est).attr('class', 'sb-line').style('stroke', c).style('stroke-width', s.tebal || 2).attr('d', ln);
    if (pra.length) {
      svg.append('path').datum(est.slice(-1).concat(pra)).attr('class', 'sb-line sb-putus').style('stroke', c)
        .style('stroke-width', s.tebal || 2).attr('d', ln);
    }
  });
  // label ujung, dijauhkan supaya tidak bertumpuk
  ujung.forEach((u) => {
    u.y = y(u.r.v);
  });
  ujung.sort((a, b) => a.y - b.y);
  for (let i = 1; i < ujung.length; i++) ujung[i].y = Math.max(ujung[i].y, ujung[i - 1].y + 14);
  for (let i = ujung.length - 1; i >= 0; i--) {
    ujung[i].y = Math.min(ujung[i].y, (i === ujung.length - 1 ? H - 28 : ujung[i + 1].y - 14));
  }
  svg.append('g').selectAll('text').data(ujung).join('text').attr('class', 'sb-end')
    .attr('x', (u) => x(u.r.t) + 6).attr('y', (u) => u.y + 4).style('fill', (u) => u.s.color || warna(series.indexOf(u.s)))
    .text((u) => u.teks);
  // tooltip
  const tip = tipBaru(el);
  const tanggal = [...new Set(all.map((r) => +r.t))].sort((a, b) => a - b);
  const garis = svg.append('line').attr('class', 'sb-hover').attr('y1', 14).attr('y2', H - 24).style('opacity', 0);
  const titik = svg.append('g');
  svg.append('rect').attr('x', ml).attr('y', 0).attr('width', Math.max(0, W - mr - ml)).attr('height', H)
    .style('fill', 'transparent')
    .on('pointermove', (ev) => {
      const [mx] = d3.pointer(ev);
      const t0 = +x.invert(mx);
      const t = tanggal[d3.minIndex(tanggal, (d) => Math.abs(d - t0))];
      const xx = x(new Date(t));
      garis.attr('x1', xx).attr('x2', xx).style('opacity', 1);
      const hit = series.map((s, i) => ({s, i, r: s.d.find((r) => +r.t === t)})).filter((h) => h.r);
      titik.selectAll('circle').data(hit).join('circle').attr('r', 4).attr('cx', xx).attr('cy', (h) => y(h.r.v))
        .style('fill', (h) => h.s.color || warna(h.i)).style('stroke', 'var(--color-panel)');
      const r0 = hit[0] && hit[0].r;
      tipIsi(tip, per(r0.periode) + (r0.jenis === 'prakiraan' ? ' · prakiraan' : ''), hit.map((h) => [
        hit.length > 1 ? h.s.color || warna(h.i) : null, h.s.name,
        F[o.fmt || 1](h.r.v) + (h.s.band ? ` (${F[1](h.r.p05)}–${F[1](h.r.p95)})` : ''),
      ]));
      const sk = el.clientWidth / W;
      tipTaruh(el, tip, xx * sk, d3.mean(hit, (h) => y(h.r.v)) * sk);
    })
    .on('pointerleave', () => {
      tip.hidden = true;
      garis.style('opacity', 0);
      titik.selectAll('circle').remove();
    });
}

// items: [{label, median, p05, p95, obs, aksen}]
function grafikRentang(el, items, o) {
  o = o || {};
  if (!items.length) return;
  const W = Math.max(260, el.clientWidth || 600);
  const rowH = 30;
  const top = 24;
  const H = top + items.length * rowH + 4;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`)
    .attr('class', 'sb-svg').attr('role', 'img').attr('aria-label', o.label || '');
  const ml = Math.min(W * 0.45, ukur(svg, 'sb-lab', items.map((d) => d.label)) + 12);
  const fm = F[o.fmt || 1];
  const mr = ukur(svg, 'sb-end', items.map((d) => fm(d.median))) + 12;
  const xmax = d3.max(items, (d) => Math.max(d.p95 == null ? d.median : d.p95, d.obs == null ? 0 : d.obs));
  const xmin = o.min == null ? 0 : o.min;
  const x = d3.scaleLinear([xmin, xmax * 1.02], [ml, W - mr]).nice();
  const ticks = x.ticks(Math.max(2, Math.floor((W - ml - mr) / 70)));
  svg.append('g').selectAll('line').data(ticks).join('line').attr('class', 'sb-grid')
    .attr('x1', (t) => x(t)).attr('x2', (t) => x(t)).attr('y1', top - 6).attr('y2', H);
  svg.append('g').selectAll('text').data(ticks).join('text').attr('class', 'sb-tick').attr('text-anchor', 'middle')
    .attr('x', (t) => x(t)).attr('y', 12).text(x.tickFormat());
  const g = svg.append('g').selectAll('g').data(items).join('g').attr('transform', (d, i) => `translate(0,${top + i * rowH + rowH / 2})`);
  g.append('text').attr('class', 'sb-lab').attr('x', ml - 10).attr('y', 4).attr('text-anchor', 'end').text((d) => d.label);
  g.filter((d) => d.p05 != null).append('line').attr('class', 'sb-whisk').attr('x1', (d) => x(d.p05)).attr('x2', (d) => x(d.p95))
    .style('stroke', (d) => (d.aksen === false ? 'var(--cds-chart-muted)' : d.warna || warna(0)));
  g.append('circle').attr('r', 5).attr('cx', (d) => x(d.median))
    .style('fill', (d) => (d.aksen === false ? 'var(--cds-chart-muted)' : d.warna || warna(0)));
  g.filter((d) => d.obs != null).append('path').attr('transform', (d) => `translate(${x(d.obs)},0)`)
    .attr('d', d3.symbol(d3.symbolDiamond, 70)).style('fill', 'var(--color-fg)');
  g.append('text').attr('class', 'sb-end').attr('x', (d) => x(d.p95 == null ? d.median : Math.max(d.p95, d.obs || 0)) + 8)
    .attr('y', 4).text((d) => fm(d.median));
  const tip = tipBaru(el);
  g.append('rect').attr('x', 0).attr('y', -rowH / 2).attr('width', W).attr('height', rowH).style('fill', 'transparent')
    .on('pointermove', (ev, d) => {
      const b = [['', 'Median', fm(d.median)]];
      if (d.p05 != null) b.push(['', 'Rentang 90%', fm(d.p05) + '–' + fm(d.p95)]);
      if (d.obs != null) b.push(['', o.obsNama || 'Amatan', fm(d.obs)]);
      tipIsi(tip, d.label, b.map(([, n, v]) => [null, n, v]));
      const [mx, my] = d3.pointer(ev, svg.node());
      const sk = el.clientWidth / W;
      tipTaruh(el, tip, mx * sk, my * sk);
    })
    .on('pointerleave', () => {
      tip.hidden = true;
    });
}

function grafikJembatan(el, items) {
  const W = Math.max(260, el.clientWidth || 600);
  const rowH = 26;
  const top = 24;
  const H = top + items.length * rowH + 4;
  const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`)
    .attr('class', 'sb-svg').attr('role', 'img').attr('aria-label', 'Jembatan stok nasional');
  let jalan = 0;
  const d = items.map((r) => {
    const a = r.jenis === 'total' ? 0 : jalan;
    const b = r.jenis === 'total' ? r.nilai : jalan + r.nilai;
    jalan = r.jenis === 'total' ? r.nilai : b;
    return Object.assign({a, b}, r);
  });
  const ml = Math.min(W * 0.5, ukur(svg, 'sb-lab', d.map((r) => r.langkah)) + 12);
  const lab = (r) => (r.jenis === 'total' ? F[1](r.nilai) : F.s1(r.nilai));
  const mr = ukur(svg, 'sb-end', d.map(lab)) + 10;
  const x = d3.scaleLinear([0, d3.max(d, (r) => Math.max(r.a, r.b))], [ml, W - mr]).nice();
  const ticks = x.ticks(Math.max(2, Math.floor((W - ml - mr) / 60)));
  svg.append('g').selectAll('line').data(ticks).join('line').attr('class', 'sb-grid')
    .attr('x1', (t) => x(t)).attr('x2', (t) => x(t)).attr('y1', top - 6).attr('y2', H);
  svg.append('g').selectAll('text').data(ticks).join('text').attr('class', 'sb-tick').attr('text-anchor', 'middle')
    .attr('x', (t) => x(t)).attr('y', 12).text(x.tickFormat());
  const g = svg.append('g').selectAll('g').data(d).join('g').attr('transform', (r, i) => `translate(0,${top + i * rowH})`);
  g.append('text').attr('class', 'sb-lab').attr('x', ml - 10).attr('y', rowH / 2 + 4).attr('text-anchor', 'end').text((r) => r.langkah);
  g.append('rect').attr('x', (r) => x(Math.min(r.a, r.b))).attr('y', 4).attr('height', rowH - 8).attr('rx', 2)
    .attr('width', (r) => Math.max(1, Math.abs(x(r.b) - x(r.a))))
    .style('fill', (r) => (r.jenis === 'total' ? warna(0) : r.nilai >= 0 ? warna(2) : warna(3)));
  g.append('text').attr('class', 'sb-end').attr('x', (r) => x(Math.max(r.a, r.b)) + 6).attr('y', rowH / 2 + 4).text(lab);
}

// ---------- gambar per halaman ----------
grafik('g-nasional', ['stok'], (el) => grafikGaris(el, [
  {name: 'Total', rows: seri('nasional', 'INDONESIA', 'total'), band: true, color: warna(0)},
  {name: 'Swasta', rows: seri('nasional', 'INDONESIA', 'swasta'), color: warna(1)},
  {name: 'BULOG', rows: seri('nasional', 'INDONESIA', 'bulog'), color: warna(2)},
], {label: 'Stok beras nasional per bulan, juta ton'}));
grafik('g-pulau', ['stok'], (el) => {
  const ix = stokIdx();
  const it = [...new Set(rows('stok').filter((r) => r.tingkat === 'pulau').map((r) => r.wilayah))]
    .map((w) => ix.get(`pulau|${w}|2026-09|total`)).filter(Boolean)
    .map((r) => ({label: r.nama, median: r.median, p05: r.p05, p95: r.p95}));
  grafikRentang(el, it, {label: 'Stok per pulau Sep 2026'});
});
grafik('g-komponen', ['stok'], (el) => {
  const ix = stokIdx();
  const it = ['rumah_tangga', 'bulog', 'pedagang', 'penggilingan', 'horeka']
    .map((k) => ix.get(`nasional|INDONESIA|2026-09|${k}`)).filter(Boolean)
    .map((r) => ({label: KOMP[r.komponen], median: r.median, p05: r.p05, p95: r.p95}));
  grafikRentang(el, it, {label: 'Komponen stok nasional Sep 2026'});
});

// halaman wilayah
dash.draw('pilih-periode', (sel) => {
  const r = rows('stok');
  const ps = r ? [...new Set(r.map((x) => x.periode))].sort().reverse() : [];
  sel.replaceChildren(...ps.map((p) => new Option(per(p) + (p > '2026-09' ? ' (prakiraan)' : ''), p)));
  sel.value = P().periode;
  sel.onchange = () => dash.setParams({periode: sel.value});
});
dash.draw('wil-nama', (el) => {
  const [tk, w] = P().wil.split('|');
  const r = (rows('stok') || []).find((x) => x.tingkat === tk && x.wilayah === w);
  el.textContent = r ? r.nama + (tk === 'provinsi' ? ' (' + r.pulau + ')' : '') : '—';
});
grafik('g-wilayah', ['stok'], (el) => {
  const [tk, w] = P().wil.split('|');
  grafikGaris(el, [
    {name: 'Total', rows: seri(tk, w, 'total'), band: true, color: warna(0)},
    {name: 'Swasta', rows: seri(tk, w, 'swasta'), color: warna(1)},
    {name: 'BULOG', rows: seri(tk, w, 'bulog'), color: warna(2)},
  ], {label: 'Stok per bulan wilayah terpilih, juta ton'});
});

const urut = {};
const cariTeks = {};
const susun = (tb, data) => {
  const s = urut[tb.dataset.draw];
  let d = data;
  const q = (cariTeks[tb.dataset.draw] || '').trim().toLowerCase();
  if (q) d = d.filter((r) => Object.values(r).some((v) => typeof v === 'string' && v.toLowerCase().includes(q)));
  if (s) {
    d = d.slice().sort((a, b) => {
      const x = a[s.field];
      const y = b[s.field];
      if (x == null) return 1;
      if (y == null) return -1;
      return (typeof x === 'number' ? x - y : String(x).localeCompare(String(y), 'id')) * (s.dir === 'ascending' ? 1 : -1);
    });
  }
  return d;
};
// cols: [field, format, opsi]; opsi.bar = maksimum untuk batang di sel
const isiTabel = (tb, data, cols, key, o) => {
  o = o || {};
  tb.replaceChildren(...data.map((r) => {
    const tr = document.createElement('tr');
    tr.dataset.key = key(r);
    if (o.wil) tr.dataset.wil = o.wil(r);
    if (o.pilih && o.pilih(r)) tr.classList.add('sb-pilih');
    for (const [f, fm, op] of cols) {
      const td = document.createElement('td');
      const v = r[f];
      const teks = v == null || (typeof v === 'number' && !isFinite(v)) ? '—' : fm ? (F[fm] || F[1])(v) : String(v);
      if (fm) td.className = 'sb-num';
      if (op && op.bar && typeof v === 'number') {
        const bx = document.createElement('span');
        bx.className = 'sb-cellbar';
        const b = document.createElement('span');
        b.style.width = Math.max(0, Math.min(100, (100 * v) / op.bar)) + '%';
        bx.appendChild(b);
        const t = document.createElement('span');
        t.textContent = teks;
        td.append(bx, t);
      } else td.textContent = teks;
      tr.appendChild(td);
    }
    return tr;
  }));
};
const tabel = (name, ids, fn) => dash.draw(name, (tb) => {
  if (status(ids) !== 'ok') {
    tb.replaceChildren();
    return;
  }
  fn(tb);
});
tabel('tb-prov', ['stok'], (tb) => {
  const p = P();
  const d = rows('stok').filter((r) => r.tingkat === 'provinsi' && r.periode === p.periode && r.komponen === p.komponen);
  const mx = d3.max(d, (r) => r.p95);
  isiTabel(tb, susun(tb, d), [['nama'], ['pulau'], ['median', '2', {bar: mx}], ['p05', '2'], ['p95', '2'], ['cukup_bulan', '1']],
    (r) => r.id, {wil: (r) => 'provinsi|' + r.wilayah, pilih: (r) => p.wil === 'provinsi|' + r.wilayah});
});
tabel('tb-pulau', ['komponen_pulau'], (tb) => {
  const p = P();
  const d = rows('komponen_pulau').filter((r) => r.periode === p.periode);
  d.sort((a, b) => (a.tingkat === 'nasional') - (b.tingkat === 'nasional'));
  isiTabel(tb, d, [['nama'], ['total', '2'], ['bulog', '2'], ['swasta', '2'], ['rumah_tangga', '2'], ['penggilingan', '2'],
    ['pedagang', '2'], ['horeka', '2']], (r) => encodeURIComponent(r.periode) + ',' + encodeURIComponent(r.wilayah),
  {wil: (r) => r.tingkat + '|' + r.wilayah, pilih: (r) => p.wil === r.tingkat + '|' + r.wilayah});
});

// halaman kenapa
grafik('g-jembatan', ['jembatan'], (el) => grafikJembatan(el, rows('jembatan').slice().sort((a, b) => a.urut - b.urut)));
tabel('tb-param', ['parameter'], (tb) => {
  const d = rows('parameter').map((r) => Object.assign({}, r));
  const fm = (r) => (r.satuan === 'persen' ? '1' : r.satuan === 'proporsi' ? '3' : '2');
  tb.replaceChildren();
  for (const r of d) {
    const tr = document.createElement('tr');
    tr.dataset.key = r.id;
    for (const [f, num] of [['parameter'], ['satuan'], ['mean', 1], ['p05', 1], ['p95', 1], ['r_hat', 2]]) {
      const td = document.createElement('td');
      const v = r[f];
      td.textContent = v == null ? '—' : num ? F[num === 2 ? '3' : fm(r)](v) : String(v);
      if (num) td.className = 'sb-num';
      tr.appendChild(td);
    }
    tb.appendChild(tr);
  }
});

// halaman PAW
const VWARNA = {'Keduanya (dasar)': 0, 'Non PAW saja': 1, 'PAW saja': 3, 'Tanpa INATRADE': 4};
grafik('g-varian', ['varian'], (el) => {
  const d = rows('varian').filter((r) => r.tingkat === 'nasional' && r.periode === '2026-09').sort((a, b) => a.urut - b.urut);
  grafikRentang(el, d.map((r) => ({label: r.varian, median: r.median, p05: r.p05, p95: r.p95, warna: warna(VWARNA[r.varian] || 0)})),
    {label: 'Stok nasional Sep 2026 per varian INATRADE'});
});
grafik('g-varian-waktu', ['varian'], (el) => {
  const d = rows('varian').filter((r) => r.tingkat === 'nasional');
  const nama = [...new Set(d.sort((a, b) => a.urut - b.urut).map((r) => r.varian))];
  grafikGaris(el, nama.map((v) => ({
    name: v.replace(' (dasar)', ''), rows: d.filter((r) => r.varian === v).sort((a, b) => d3.ascending(a.periode, b.periode)),
    band: v === 'Keduanya (dasar)', color: warna(VWARNA[v] || 0), tebal: v === 'Keduanya (dasar)' ? 2.5 : 1.75,
  })), {label: 'Stok nasional per varian INATRADE, juta ton'});
});
tabel('tb-varian', ['varian_pulau'], (tb) => {
  const d = rows('varian_pulau').slice().sort((a, b) => (a.tingkat === 'nasional') - (b.tingkat === 'nasional'));
  isiTabel(tb, d, [['wilayah'], ['dasar', '2'], ['non_paw', '2'], ['paw', '2'], ['tanpa_inatrade', '2'], ['non_paw_persen', 'spct'],
    ['paw_persen', 'spct'], ['tanpa_persen', 'spct']], (r) => r.wilayah);
});
dash.draw('pulau-goyah', (el) => {
  const d = (rows('varian_pulau') || []).filter((r) => r.tingkat === 'pulau');
  if (!d.length) {
    el.textContent = '—';
    return;
  }
  const r = d3.greatest(d, (x) => Math.max(Math.abs(x.non_paw_persen), Math.abs(x.paw_persen)));
  const k = Math.abs(r.paw_persen) >= Math.abs(r.non_paw_persen) ? ['PAW saja', r.paw_persen] : ['Non PAW saja', r.non_paw_persen];
  el.textContent = `${r.wilayah} (${k[0]} ${F.spct(k[1])})`;
});
tabel('tb-lebar', ['lebar_interval'], (tb) => {
  isiTabel(tb, rows('lebar_interval'), [['nama'], ['pulau'], ['median', '2'], ['lebar', '2'], ['lebar_relatif', 'pct'],
    ['porsi_lebar', 'pct1']], (r) => r.id);
});
dash.draw('porsi-top', (el) => {
  const d = rows('lebar_interval');
  el.textContent = d ? F.pct(d.slice(0, 7).reduce((s, r) => s + r.porsi_lebar, 0)) : '—';
});

// halaman uji
grafik('g-validasi', ['uji'], (el) => grafikRentang(el, rows('uji').filter((r) => r.jenis === 'validasi')
  .map((r) => ({label: per(r.periode) + (r.uji.includes('disembunyikan') ? ' (holdout)' : ''), median: r.median, p05: r.p05, p95: r.p95, obs: r.amatan})),
{label: 'Prediksi model vs amatan survei', obsNama: 'Amatan survei'}));
grafik('g-sensitif', ['uji'], (el) => grafikRentang(el, rows('uji').filter((r) => r.jenis === 'sensitivitas')
  .map((r) => ({label: r.uji, median: r.median, p05: r.p05, p95: r.p95, warna: r.uji.includes('dasar') ? warna(0) : warna(1)})),
{label: 'Sensitivitas kendala swasta tidak negatif'}));
tabel('tb-uji', ['uji'], (tb) => isiTabel(tb, rows('uji'), [['uji'], ['periode', 'per'], ['amatan', '2'], ['median', '2'], ['p05', '2'], ['p95', '2']], (r) => r.id));
grafik('g-banding', ['stok', 'pembanding'], (el) => {
  const pb = rows('pembanding');
  const est = seri('nasional', 'INDONESIA', 'total');
  grafikGaris(el, [
    {name: 'Model', rows: est, band: true, color: warna(0)},
    {name: 'Neraca Bapanas', rows: pb.filter((r) => r.sumber === 'Neraca Bapanas'), f: 'nilai', kind: 'titik', color: warna(3), simbol: d3.symbolSquare},
    {name: 'USDA PSD', rows: pb.filter((r) => r.sumber === 'USDA PSD'), f: 'nilai', kind: 'titik', color: warna(1), simbol: d3.symbolTriangle},
    {name: 'Survei', rows: pb.filter((r) => r.sumber.startsWith('Survei')), f: 'nilai', kind: 'titik', color: 'var(--color-fg)', simbol: d3.symbolDiamond},
  ], {label: 'Model vs pembanding, juta ton', h: 320});
});
tabel('tb-banding', ['banding'], (tb) => isiTabel(tb, rows('banding'), [['sumber'], ['periode', 'per'], ['nilai', '2'], ['model', '2'], ['rasio', '2'], ['catatan']], (r) => r.id));

// halaman prakiraan
grafik('g-prakiraan', ['stok'], (el) => {
  const f = (k) => seri('nasional', 'INDONESIA', k).filter((r) => r.periode >= '2025-10');
  grafikGaris(el, [
    {name: 'Total', rows: f('total'), band: true, color: warna(0)},
    {name: 'Swasta', rows: f('swasta'), color: warna(1)},
    {name: 'BULOG', rows: f('bulog'), color: warna(2)},
  ], {label: 'Stok nasional Okt 2025 sampai prakiraan Des 2026, juta ton'});
});
grafik('g-pulau-pra', ['stok'], (el) => {
  const ix = stokIdx();
  const b = P().bulan;
  const it = [...new Set(rows('stok').filter((r) => r.tingkat === 'pulau').map((r) => r.wilayah))]
    .map((w) => ix.get(`pulau|${w}|${b}|total`)).filter(Boolean)
    .map((r) => ({label: r.nama, median: r.median, p05: r.p05, p95: r.p95}));
  grafikRentang(el, it, {label: 'Prakiraan stok per pulau'});
});
tabel('tb-risiko', ['risiko'], (tb) => {
  const b = P().bulan;
  const d = rows('risiko').filter((r) => r.periode === b && r.wilayah !== 'INDONESIA');
  if (!urut['tb-risiko']) d.sort((a, x) => x.peluang_kurang_1_bulan - a.peluang_kurang_1_bulan || a.cukup_bulan - x.cukup_bulan);
  isiTabel(tb, susun(tb, d), [['nama'], ['pulau'], ['cukup_bulan', '1'], ['peluang_kurang_1_bulan', 'pct', {bar: 1}]], (r) => r.id);
});
dash.draw('top-risiko', (el) => {
  const d = rows('risiko');
  if (!d) {
    el.textContent = '—';
    return;
  }
  const b = P().bulan;
  const t = d.filter((r) => r.periode === b && r.wilayah !== 'INDONESIA')
    .sort((a, x) => x.peluang_kurang_1_bulan - a.peluang_kurang_1_bulan).slice(0, 4);
  el.textContent = t.map((r) => `${r.nama} (${F.pct(r.peluang_kurang_1_bulan)})`).join(', ');
});
dash.draw('bulan-nama', (el) => {
  el.textContent = per(P().bulan);
});

// tabel teks
tabel('tb-sumber', ['sumber'], (tb) => isiTabel(tb, rows('sumber'), [['data'], ['isi'], ['cakupan'], ['akses'], ['dipakai_untuk']], (r) => r.id));
tabel('tb-kualitas', ['kualitas'], (tb) => isiTabel(tb, rows('kualitas'), [['indikator'], ['nilai']], (r) => r.id));

// ---------- tab, filter, urut, cari ----------
let tab = 'ringkasan';
const tampil = () => {
  for (const s of document.querySelectorAll('.sb-page')) s.hidden = s.id !== tab;
  for (const b of document.querySelectorAll('.sb-tab')) b.setAttribute('aria-selected', String(b.dataset.tab === tab));
};
const awal = location.hash.slice(1);
for (const s of document.querySelectorAll('.sb-page')) if (s.id === awal) tab = awal;
for (const b of document.querySelectorAll('.sb-tab')) {
  b.addEventListener('click', () => {
    tab = b.dataset.tab;
    tampil();
    dash.setLink(tab);
    const nama = new Set();
    for (const s of document.querySelectorAll('.sb-page')) {
      if (s.id === tab) for (const e of s.querySelectorAll('[data-draw]')) nama.add(e.dataset.draw);
    }
    nama.forEach((n) => dash.draw(n));
  });
}
for (const sel of document.querySelectorAll('.sb-komponen')) {
  sel.addEventListener('change', () => dash.setParams({komponen: sel.value}));
}
for (const sel of document.querySelectorAll('.sb-bulan')) {
  sel.addEventListener('change', () => dash.setParams({bulan: sel.value}));
}
for (const b of document.querySelectorAll('.sb-nasional')) {
  b.addEventListener('click', () => dash.setParams({wil: null}));
}
for (const t of document.querySelectorAll('.sb-klik')) {
  t.addEventListener('click', (ev) => {
    const tr = ev.target.closest('tr[data-wil]');
    if (tr) {
      dash.setParams({wil: tr.dataset.wil});
      const box = document.getElementById('kartu-wilayah');
      if (box) box.scrollIntoView({behavior: 'smooth', block: 'start'});
    }
  });
}
for (const t of document.querySelectorAll('table.sb-urut')) {
  for (const btn of t.querySelectorAll('th .sb-sort')) {
    btn.addEventListener('click', () => {
      const th = btn.closest('th');
      const tb = t.querySelector('tbody[data-draw]');
      if (!th || !tb) return;
      const lama = urut[tb.dataset.draw];
      const dir = lama && lama.field === th.dataset.field && lama.dir === 'descending' ? 'ascending' : 'descending';
      urut[tb.dataset.draw] = {field: th.dataset.field, dir};
      for (const h of t.querySelectorAll('th')) h.setAttribute('aria-sort', h === th ? dir : 'none');
      dash.draw(tb.dataset.draw);
    });
  }
}
for (const inp of document.querySelectorAll('.sb-cari')) {
  inp.addEventListener('input', () => {
    cariTeks[inp.dataset.untuk] = inp.value;
    dash.draw(inp.dataset.untuk);
  });
}
dash.onData(() => {
  tampil();
  const p = P();
  for (const sel of document.querySelectorAll('.sb-komponen')) sel.value = p.komponen;
  for (const sel of document.querySelectorAll('.sb-bulan')) sel.value = p.bulan;
  for (const b of document.querySelectorAll('.sb-nasional')) b.disabled = p.wil === DEF.wil;
});
