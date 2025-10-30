(() => {
  const $ = (id) => document.getElementById(id);
  const tz = $('tzMode');
  const nowBtn = $('nowBtn');
  const tsInput = $('tsInput');
  const dateInput = $('dateInput');
  const tsToDate = $('tsToDate');
  const dateToTs = $('dateToTs');
  const clearTs = $('clearTs');
  const isoOut = $('isoOut');
  const readableOut = $('readableOut');
  const secOut = $('secOut');
  const msOut = $('msOut');
  if (!tz) return;

  const toDate = (ts) => {
    // Accept seconds or ms
    let n = Number(ts);
    if (!Number.isFinite(n)) return null;
    if (ts.toString().length <= 10) n = n * 1000;
    const d = new Date(n);
    if (isNaN(d.getTime())) return null;
    return d;
  };

  const fmt = (d) => {
    const pad = (x) => x.toString().padStart(2, '0');
    const y = tz.value === 'utc' ? d.getUTCFullYear() : d.getFullYear();
    const mo = pad(tz.value === 'utc' ? d.getUTCMonth()+1 : d.getMonth()+1);
    const da = pad(tz.value === 'utc' ? d.getUTCDate() : d.getDate());
    const h = pad(tz.value === 'utc' ? d.getUTCHours() : d.getHours());
    const mi = pad(tz.value === 'utc' ? d.getUTCMinutes() : d.getMinutes());
    const s = pad(tz.value === 'utc' ? d.getUTCSeconds() : d.getSeconds());
    const iso = tz.value === 'utc' ? d.toISOString() : new Date(d.getTime() - d.getTimezoneOffset()*60000).toISOString().replace('Z','');
    return { iso, readable: `${y}-${mo}-${da} ${h}:${mi}:${s}` };
  };

  const show = (d) => {
    if (!d) { isoOut.textContent='-'; readableOut.textContent='-'; secOut.textContent='-'; msOut.textContent='-'; return; }
    const { iso, readable } = fmt(d);
    isoOut.textContent = iso;
    readableOut.textContent = readable;
    secOut.textContent = Math.floor(d.getTime()/1000).toString();
    msOut.textContent = d.getTime().toString();
  };

  nowBtn?.addEventListener('click', () => { show(new Date()); });
  tsToDate?.addEventListener('click', () => { show(toDate(tsInput.value.trim())); });
  dateToTs?.addEventListener('click', () => {
    const val = dateInput.value.trim();
    if (!val) { show(null); return; }
    // Try parsing as ISO or "YYYY-MM-DD HH:mm:ss"
    let d = new Date(val);
    if (isNaN(d.getTime())) {
      const m = /^\s*(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})\s*$/.exec(val);
      if (m) {
        if (tz.value === 'utc') {
          d = new Date(Date.UTC(+m[1], +m[2]-1, +m[3], +m[4], +m[5], +m[6]));
        } else {
          d = new Date(+m[1], +m[2]-1, +m[3], +m[4], +m[5], +m[6]);
        }
      }
    }
    if (isNaN(d.getTime())) { show(null); return; }
    show(d);
  });
  clearTs?.addEventListener('click', () => { tsInput.value=''; dateInput.value=''; show(null); });
})();


