(() => {
  const $ = (id) => document.getElementById(id);
  const csvIn = $('csvInput');
  const jsonIn = $('jsonInput');
  const out = $('csvJsonOutput');
  const csvToJsonBtn = $('csvToJson');
  const jsonToCsvBtn = $('jsonToCsv');
  const clearCsv = $('clearCsv');
  const clearJson = $('clearJson');
  const hasHeader = $('hasHeader');
  const delimiter = $('delimiter');
  if (!csvIn) return;

  const parseCSV = (text, delim, header) => {
    const rows = [];
    let current = '';
    let row = [];
    let inQuotes = false;
    const d = delim || ',';
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (inQuotes) {
        if (c === '"') {
          if (text[i+1] === '"') { current += '"'; i++; } else { inQuotes = false; }
        } else { current += c; }
      } else {
        if (c === '"') { inQuotes = true; }
        else if (c === d) { row.push(current); current = ''; }
        else if (c === '\n') { row.push(current); rows.push(row); row = []; current = ''; }
        else if (c === '\r') { /* ignore */ }
        else { current += c; }
      }
    }
    if (current.length || row.length) { row.push(current); rows.push(row); }
    if (!rows.length) return [];
    if (!header) return rows;
    const headers = rows[0];
    const out = rows.slice(1).map(r => {
      const obj = {};
      headers.forEach((h, idx) => { obj[h] = r[idx] ?? ''; });
      return obj;
    });
    return out;
  };

  const toCSV = (data, delim, header) => {
    const d = delim || ',';
    const escape = (s) => {
      const str = s == null ? '' : String(s);
      return (str.includes('"') || str.includes('\n') || str.includes('\r') || str.includes(d))
        ? '"' + str.replace(/"/g, '""') + '"' : str;
    };
    if (Array.isArray(data) && data.length && typeof data[0] === 'object') {
      const headers = header ? Object.keys(data[0]) : null;
      const lines = [];
      if (headers) lines.push(headers.map(escape).join(d));
      data.forEach(obj => {
        const row = (headers || Object.keys(obj)).map(k => escape(obj[k]));
        lines.push(row.join(d));
      });
      return lines.join('\n');
    } else if (Array.isArray(data)) {
      return data.map(r => r.map(escape).join(d)).join('\n');
    }
    return '';
  };

  csvToJsonBtn?.addEventListener('click', () => {
    try {
      const result = parseCSV(csvIn.value || '', delimiter.value || ',', hasHeader.checked);
      out.value = JSON.stringify(result, null, 2);
    } catch (e) {
      out.value = 'Conversion error: ' + e.message;
    }
  });

  jsonToCsvBtn?.addEventListener('click', () => {
    try {
      const data = JSON.parse(jsonIn.value || '[]');
      out.value = toCSV(data, delimiter.value || ',', hasHeader.checked);
    } catch (e) {
      out.value = 'Conversion error: ' + e.message;
    }
  });

  clearCsv?.addEventListener('click', () => { csvIn.value = ''; });
  clearJson?.addEventListener('click', () => { jsonIn.value = ''; });
})();


