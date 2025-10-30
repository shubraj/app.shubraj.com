(() => {
  const $ = (id) => document.getElementById(id);
  const cidrInput = $('cidrInput');
  const ipInput = $('ipInput');
  const maskInput = $('maskInput');
  const calcBtn = $('calcBtn');
  const clearBtn = $('clearCidr');
  const netOut = $('netOut');
  const maskOut = $('maskOut');
  const wildOut = $('wildOut');
  const bcastOut = $('bcastOut');
  const firstOut = $('firstOut');
  const lastOut = $('lastOut');
  const hostsOut = $('hostsOut');
  if (!calcBtn) return;

  const toInt = (ip) => ip.split('.').reduce((a, o) => (a << 8) + (o|0), 0) >>> 0;
  const toIp = (n) => [24,16,8,0].map(shift => ((n >>> shift) & 255)).join('.');
  const maskFromLen = (len) => (len === 0 ? 0 : ((0xFFFFFFFF << (32 - len)) >>> 0));
  const wildcardFromMask = (mask) => (~mask) >>> 0;

  const calc = () => {
    let ipStr = ipInput.value.trim();
    let lenStr = maskInput.value.trim();
    if (cidrInput.value.trim()) {
      const m = cidrInput.value.trim().match(/^\s*([0-9]{1,3}(?:\.[0-9]{1,3}){3})\s*\/\s*([0-9]{1,2})\s*$/);
      if (!m) return show('-', '-', '-', '-', '-', '-');
      ipStr = m[1];
      lenStr = m[2];
    }
    const len = Math.max(0, Math.min(32, parseInt(lenStr || '0', 10)));
    if (!/^\d+\.\d+\.\d+\.\d+$/.test(ipStr)) return show('-', '-', '-', '-', '-', '-');
    const ip = toInt(ipStr);
    const mask = maskFromLen(len);
    const net = (ip & mask) >>> 0;
    const wild = wildcardFromMask(mask);
    const bcast = (net | wild) >>> 0;
    let first = net, last = bcast, hosts = 0;
    if (len === 32) {
      first = last = ip;
      hosts = 1;
    } else if (len === 31) {
      // point-to-point
      first = net; last = bcast; hosts = 2;
    } else {
      first = (net + 1) >>> 0;
      last = (bcast - 1) >>> 0;
      hosts = Math.max(0, (1 << (32 - len)) - 2);
    }
    show(`${toIp(net)}/${len}`, toIp(mask), toIp(wild), toIp(bcast), toIp(first), toIp(last), hosts.toString());
  };

  const show = (net, mask, wild, bcast, first, last, hosts='-') => {
    netOut.textContent = net;
    maskOut.textContent = mask;
    wildOut.textContent = wild;
    bcastOut.textContent = bcast;
    firstOut.textContent = first;
    lastOut.textContent = last;
    hostsOut.textContent = hosts;
  };

  calcBtn.addEventListener('click', calc);
  clearBtn.addEventListener('click', () => {
    cidrInput.value=''; ipInput.value=''; maskInput.value=''; show('-', '-', '-', '-', '-', '-', '-');
  });
})();


