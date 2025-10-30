(() => {
  const $ = (id) => document.getElementById(id);
  const input = $('urlInput');
  const output = $('urlOutput');
  const encodeBtn = $('encodeBtn');
  const decodeBtn = $('decodeBtn');
  const copyBtn = $('copyBtn');
  const clearBtn = $('clearBtn');

  if (!input) return;

  const encode = () => {
    try {
      output.value = encodeURIComponent(input.value);
    } catch (e) {
      output.value = 'Encoding error: ' + e.message;
    }
  };

  const decode = () => {
    try {
      output.value = decodeURIComponent(input.value);
    } catch (e) {
      // Try a lenient decode: replace lone % with %25
      try {
        const safe = input.value.replace(/%(?![0-9a-fA-F]{2})/g, '%25');
        output.value = decodeURIComponent(safe);
      } catch (e2) {
        output.value = 'Decoding error: ' + e2.message;
      }
    }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(output.value);
      copyBtn.textContent = 'Copied!';
      setTimeout(() => (copyBtn.textContent = 'Copy Output'), 1000);
    } catch {}
  };

  const clearAll = () => {
    input.value = '';
    output.value = '';
  };

  encodeBtn?.addEventListener('click', encode);
  decodeBtn?.addEventListener('click', decode);
  copyBtn?.addEventListener('click', copy);
  clearBtn?.addEventListener('click', clearAll);
})();


