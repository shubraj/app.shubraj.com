(() => {
  const $ = (id) => document.getElementById(id);
  const input = $('caseInput');
  const output = $('caseOutput');
  const btn = (id, fn) => $(id)?.addEventListener('click', () => { output.value = fn(input.value || ''); });
  if (!input) return;

  const words = (s) => {
    // Split on non-alphanum and boundaries: HelloWorld -> [Hello, World]
    return (s || '')
      .replace(/[_-]+/g, ' ')
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      .split(/[^A-Za-z0-9]+/)
      .filter(Boolean);
  };

  const lower = (arr) => arr.map(w => w.toLowerCase());
  const cap = (w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();

  const camel = (s) => {
    const w = words(s);
    if (!w.length) return '';
    return w[0].toLowerCase() + w.slice(1).map(cap).join('');
  };
  const pascal = (s) => words(s).map(cap).join('');
  const snake = (s) => lower(words(s)).join('_');
  const kebab = (s) => lower(words(s)).join('-');
  const constant = (s) => words(s).map(w => w.toUpperCase()).join('_');
  const title = (s) => words(s).map((w,i) => cap(w)).join(' ');
  const sentence = (s) => {
    const t = (s || '').trim().toLowerCase();
    return t ? t.charAt(0).toUpperCase() + t.slice(1) : '';
  };

  btn('toCamel', camel);
  btn('toPascal', pascal);
  btn('toSnake', snake);
  btn('toKebab', kebab);
  btn('toConstant', constant);
  btn('toTitle', title);
  btn('toSentence', sentence);

  $('clearCase')?.addEventListener('click', () => { input.value=''; output.value=''; });
  $('copyCase')?.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(output.value || ''); } catch {}
  });
})();


