(() => {
  const $ = (id) => document.getElementById(id);
  const input = $('jwtInput');
  const btn = $('jwtDecodeBtn');
  const clearBtn = $('jwtClearBtn');
  const outH = $('jwtHeader');
  const outP = $('jwtPayload');
  const outS = $('jwtSignature');
  const err = $('jwtError');
  if (!input) return;

  const b64urlToUtf8 = (str) => {
    try {
      const pad = str.length % 4 === 2 ? '==': (str.length % 4 === 3 ? '=' : '');
      const b64 = str.replace(/-/g, '+').replace(/_/g, '/') + pad;
      const bytes = atob(b64);
      // decode UTF-8
      const utf8 = decodeURIComponent(bytes.split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      return utf8;
    } catch (e) {
      throw new Error('Invalid base64url');
    }
  };

  const decodeJWT = () => {
    err.style.display = 'none';
    outH.value = '';
    outP.value = '';
    outS.value = '';
    const token = (input.value || '').trim();
    if (!token) return;
    const parts = token.split('.');
    if (parts.length < 2) {
      err.style.display = 'block';
      err.textContent = 'Invalid JWT: expecting header.payload[.signature]';
      return;
    }
    try {
      const header = JSON.parse(b64urlToUtf8(parts[0]));
      const payload = JSON.parse(b64urlToUtf8(parts[1]));
      outH.value = JSON.stringify(header, null, 2);
      outP.value = JSON.stringify(payload, null, 2);
      outS.value = parts[2] || '';
    } catch (e) {
      err.style.display = 'block';
      err.textContent = 'Failed to decode: ' + e.message;
    }
  };

  btn?.addEventListener('click', decodeJWT);
  clearBtn?.addEventListener('click', () => {
    input.value = '';
    outH.value = '';
    outP.value = '';
    outS.value = '';
    err.style.display = 'none';
  });
})();


