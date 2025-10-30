(() => {
  const $ = (id) => document.getElementById(id);
  const out = $('idOutput');
  const genUuid = $('genUuid');
  const genUlid = $('genUlid');
  const copyId = $('copyId');
  const clearId = $('clearId');
  const batchCount = $('batchCount');
  const genBatch = $('genBatch');
  const copyBatch = $('copyBatch');
  const batchOut = $('batchOutput');
  if (!out) return;

  const uuidv4 = () => {
    const buf = new Uint8Array(16);
    crypto.getRandomValues(buf);
    // Per RFC 4122
    buf[6] = (buf[6] & 0x0f) | 0x40; // version 4
    buf[8] = (buf[8] & 0x3f) | 0x80; // variant
    const hex = [...buf].map(b => b.toString(16).padStart(2, '0')).join('');
    return `${hex.slice(0,8)}-${hex.slice(8,12)}-${hex.slice(12,16)}-${hex.slice(16,20)}-${hex.slice(20)}`;
  };

  // ULID per https://github.com/ulid/spec
  const ENCODING = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
  const encodeCrockford = (buffer) => {
    let out = '';
    let bits = 0;
    let value = 0;
    for (let i = 0; i < buffer.length; i++) {
      value = (value << 8) | buffer[i];
      bits += 8;
      while (bits >= 5) {
        out += ENCODING[(value >>> (bits - 5)) & 31];
        bits -= 5;
      }
    }
    if (bits > 0) out += ENCODING[(value << (5 - bits)) & 31];
    return out;
  };

  const ulid = () => {
    const time = Date.now();
    // 48-bit time = 6 bytes
    const timeBuf = new Uint8Array(6);
    let t = time;
    for (let i = 5; i >= 0; i--) {
      timeBuf[i] = t & 0xff;
      t = Math.floor(t / 256);
    }
    // 80-bit randomness = 10 bytes
    const rand = new Uint8Array(10);
    crypto.getRandomValues(rand);
    const id = new Uint8Array(16);
    id.set(timeBuf, 0);
    id.set(rand, 6);
    // Base32 crockford -> 26 chars
    const enc = encodeCrockford(id).slice(0, 26);
    return enc;
  };

  genUuid?.addEventListener('click', () => { out.value = uuidv4(); });
  genUlid?.addEventListener('click', () => { out.value = ulid(); });
  copyId?.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(out.value); copyId.textContent='Copied!'; setTimeout(()=>copyId.textContent='Copy',800);} catch {}
  });
  clearId?.addEventListener('click', () => { out.value=''; });

  genBatch?.addEventListener('click', () => {
    const n = parseInt(batchCount.value || '1', 10);
    const list = [];
    for (let i=0;i<n;i++) list.push(uuidv4());
    batchOut.value = list.join('\n');
  });
  copyBatch?.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(batchOut.value); copyBatch.textContent='Copied!'; setTimeout(()=>copyBatch.textContent='Copy All',800);} catch {}
  });
})();


