#!/usr/bin/env node
// Lee el libro consolidado de Equiduct MarketViewer para un ISIN y un tamaño de orden.
// Uso: node scripts/equiduct.js <ISIN> <MIC_ORIGEN> [YYYYMMDD para modo replay]
// MIC_ORIGEN: XETR, XPAR, XAMS, XLON, MTAA, XMAD, XSWX/XVTX, XSTO, XCSE, XOSL, XHEL, XBRU, XLIS, XWBO, XDUB
// Salida JSON: {ok, symbol, curr, home, bid, ask, bid_size, ask_size, fuente}
// bid/ask = VBB/VBO de la fila 'Retail' (precio medio ponderado para un tamaño minorista, ~5-10k€),
// que para órdenes de ~500€ equivale a (o es ligeramente peor que) el mejor bid/ask: conservador.
const { chromium } = require('playwright');
const num = s => { if (!s) return null; const v = parseFloat(String(s).replace(/[^0-9.\-]/g, '')); return isNaN(v) ? null : v; };
(async () => {
  const [isin, mic, date] = process.argv.slice(2);
  if (!isin || !mic) { console.log(JSON.stringify({ ok: false, error: 'uso: equiduct.js ISIN MIC_ORIGEN [YYYYMMDD]' })); process.exit(2); }
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const resp = await page.goto('https://api.equiduct.com/mdwebapi/instrument', { timeout: 60000 });
    const instruments = JSON.parse(await resp.text());
    const matches = Object.entries(instruments).filter(([, v]) => v.isin === isin);
    if (!matches.length) { console.log(JSON.stringify({ ok: false, error: 'ISIN no cubierto por Equiduct', isin })); return; }
    // Solo vale la línea cuya bolsa "home" sea la bolsa de origen donde operamos.
    const mics = mic.split('/');
    const sel = matches.filter(([, v]) => mics.includes(v.home));
    if (!sel.length) { console.log(JSON.stringify({ ok: false, error: 'ISIN en Equiduct pero no con home ' + mic, homes: matches.map(m => m[1].home) })); return; }
    const [symbol, meta] = sel[0];
    let url = `https://marketviewer.equiduct.com/marketviewer?symbol=${encodeURIComponent(symbol)}`;
    if (date) url += `&date=${date}`;
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    let book = null;
    for (let i = 0; i < 20 && !book; i++) {
      await page.waitForTimeout(1000);
      book = await page.evaluate(() => {
        const read = cls => {
          const t = document.querySelector('table.' + cls); if (!t) return null;
          const hdr = [...t.querySelectorAll('th')].map(x => x.innerText.trim());
          const rows = [...t.querySelectorAll('tbody tr')].filter(r => r.style.display !== 'none')
            .map(r => [...r.querySelectorAll('td')].map(td => td.innerText.trim()));
          return { hdr, rows };
        };
        const b = read('buyside'), s = read('sellside');
        if (!b || !s) return null;
        const pick = (side, label, col) => {
          const ci = side.hdr.indexOf(col), li = side.hdr.indexOf('Market Size'), si = side.hdr.indexOf('Size');
          const row = side.rows.find(r => r[li] === label);
          return row ? { price: row[ci], size: row[si] } : null;
        };
        const ub = pick(b, 'User Entered', 'VBB'), ua = pick(s, 'User Entered', 'VBO');
        const rb = pick(b, 'Retail', 'VBB'), ra = pick(s, 'Retail', 'VBO');
        if (!(ub && ub.price && ub.price !== '-') && !(rb && rb.price && rb.price !== '-')) return null;
        return { ub, ua, rb, ra };
      });
    }
    if (!book) { console.log(JSON.stringify({ ok: false, error: 'libro vacío (mercado cerrado o sin datos)', symbol })); return; }
    const use = (u, r) => (r && num(r.price)) ? r : u;
    const b = use(book.ub, book.rb), a = use(book.ua, book.ra);
    console.log(JSON.stringify({ ok: true, symbol, isin, curr: meta.curr, home: meta.home, bid: num(b && b.price), ask: num(a && a.price),
      bid_size: num(b && b.size), ask_size: num(a && a.size), fuente: (b === book.rb ? 'Retail' : 'User Entered'), modo: date ? 'replay ' + date : 'live' }));
  } catch (e) {
    console.log(JSON.stringify({ ok: false, error: String(e).slice(0, 300) }));
  } finally { await browser.close(); }
})();
