(() => {
  const $ = (id) => document.getElementById(id);
  const pat = $('regexPattern');
  const inTxt = $('regexInput');
  const err = $('regexError');
  const res = $('regexResults');
  const run = $('runRegex');
  const clr = $('clearRegex');
  const flagsEls = ['flagG','flagI','flagM','flagS','flagU','flagY'].map($);
  if (!pat) return;

  const getFlags = () => {
    const map = { flagG:'g', flagI:'i', flagM:'m', flagS:'s', flagU:'u', flagY:'y' };
    return flagsEls.filter(el => el?.checked).map(el => map[el.id]).join('');
  };

  const escapeHtml = (s) => s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));

  const render = (matches) => {
    if (!matches || matches.length === 0) { res.innerHTML = '<p>No matches.</p>'; return; }
    const parts = matches.map((m, idx) => {
      const groups = (m.groups && Object.keys(m.groups).length)
        ? `<div><strong>Groups:</strong> ${escapeHtml(JSON.stringify(m.groups))}</div>`
        : '';
      const indices = m.indices ? `<div><strong>Index:</strong> ${m.indices[0][0]}–${m.indices[0][1]}</div>` : '';
      const arr = Array.from(m).map(x => typeof x === 'string' ? x : JSON.stringify(x));
      return `<div style="margin-bottom:0.75rem;">
        <div><strong>Match ${idx+1}:</strong> ${escapeHtml(arr[0]||'')}</div>
        ${groups}
        ${indices}
        <div><strong>Captures:</strong> ${escapeHtml(JSON.stringify(arr.slice(1)))}</div>
      </div>`;
    }).join('');
    res.innerHTML = parts;
  };

  const runTest = () => {
    err.style.display = 'none';
    res.innerHTML = '<p>No matches.</p>';
    let re;
    try {
      re = new RegExp(pat.value, getFlags());
    } catch (e) {
      err.style.display = 'block';
      err.textContent = 'Invalid pattern or flags: ' + e.message;
      return;
    }
    const text = inTxt.value || '';
    const matches = [];
    if (re.global) {
      // Use matchAll for captures; enable indices if supported
      try {
        for (const m of text.matchAll(re)) matches.push(m);
      } catch {
        // Fallback without matchAll (older engines)
        let m;
        while ((m = re.exec(text)) !== null) matches.push(m);
      }
    } else {
      const m = re.exec(text);
      if (m) matches.push(m);
    }
    render(matches);
  };

  run?.addEventListener('click', runTest);
  clr?.addEventListener('click', () => { pat.value=''; inTxt.value=''; res.innerHTML='<p>No matches yet.</p>'; err.style.display='none'; });
})();


