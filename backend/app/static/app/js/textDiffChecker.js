(() => {
  const $ = (id) => document.getElementById(id);
  const left = $('diffLeft');
  const right = $('diffRight');
  const res = $('diffResult');
  const compare = $('compareBtn');
  const swap = $('swapBtn');
  const clear = $('clearDiff');
  const ignoreCase = $('ignoreCase');
  const ignoreWs = $('ignoreWs');
  if (!left) return;

  const preprocess = (s) => {
    let t = s || '';
    if (ignoreCase.checked) t = t.toLowerCase();
    if (ignoreWs.checked) t = t.replace(/[\t ]+/g, ' ').trim();
    return t;
  };

  // Simple LCS-based line diff
  const diffLines = (aText, bText) => {
    const a = aText.split(/\r?\n/);
    const b = bText.split(/\r?\n/);
    const n = a.length, m = b.length;
    const dp = Array.from({length: n+1}, () => new Array(m+1).fill(0));
    for (let i=n-1;i>=0;i--) {
      for (let j=m-1;j>=0;j--) {
        if (a[i] === b[j]) dp[i][j] = dp[i+1][j+1] + 1; else dp[i][j] = Math.max(dp[i+1][j], dp[i][j+1]);
      }
    }
    const out = [];
    let i=0,j=0;
    while (i<n && j<m) {
      if (a[i] === b[j]) { out.push({type:'eq', text:a[i]}); i++; j++; }
      else if (dp[i+1][j] >= dp[i][j+1]) { out.push({type:'del', text:a[i]}); i++; }
      else { out.push({type:'add', text:b[j]}); j++; }
    }
    while (i<n) { out.push({type:'del', text:a[i++]}); }
    while (j<m) { out.push({type:'add', text:b[j++]}); }
    return out;
  };

  const escapeHtml = (s) => (s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));

  const render = (ops) => {
    if (!ops.length) { res.innerHTML = '<p>No differences.</p>'; return; }
    const lines = ops.map(op => {
      const sign = op.type === 'add' ? '+' : (op.type === 'del' ? '-' : ' ');
      const cls = op.type === 'add' ? 'bg-add' : (op.type === 'del' ? 'bg-del' : '');
      return `<div class="diff-line ${cls}"><code>${sign} ${escapeHtml(op.text)}</code></div>`;
    }).join('');
    res.innerHTML = `<div class="diff-view">${lines}</div>`;
  };

  compare?.addEventListener('click', () => {
    const a = preprocess(left.value);
    const b = preprocess(right.value);
    render(diffLines(a, b));
  });
  swap?.addEventListener('click', () => {
    const t = left.value; left.value = right.value; right.value = t;
  });
  clear?.addEventListener('click', () => {
    left.value = ''; right.value = ''; res.innerHTML = '<p>No comparison yet.</p>';
  });
})();


