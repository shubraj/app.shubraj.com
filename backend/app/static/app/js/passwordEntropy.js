(() => {
  const $ = (id) => document.getElementById(id);
  const input = $('pwInput');
  const bitsOut = $('bitsOut');
  const poolTotal = $('poolTotal');
  const resultTag = $('resultTag');
  const hasLower = $('hasLower');
  const hasUpper = $('hasUpper');
  const hasDigit = $('hasDigit');
  const hasShift = $('hasShift');
  const hasOther = $('hasOther');
  const showPw = $('showPw');
  const clearPw = $('clearPw');
  if (!input) return;

  const SHIFTS = ')!@#$%^&*('; // shift + 0-9 typical US layout
  const OTHER = '~`-_=+[]{}|;:\",.<>/?\'';
  const uniq = (s) => Array.from(new Set(s.split(''))).join('');

  const estimate = (pwd) => {
    const lower = /[a-z]/.test(pwd);
    const upper = /[A-Z]/.test(pwd);
    const digit = /[0-9]/.test(pwd);
    const shiftClass = /[)!@#$%^&*(]/; // Shift+0-9 symbols
    const shift = shiftClass.test(pwd);
    // Other symbols are any non-alphanumeric not part of the shift set
    const other = /[^A-Za-z0-9]/.test(pwd.replace(shiftClass, ''));
    let pool = 0;
    if (lower) pool += 26;
    if (upper) pool += 26;
    if (digit) pool += 10;
    if (shift) pool += 10;
    if (other) pool += 23;
    const bits = pwd.length ? (pwd.length * Math.log2(Math.max(1, pool))) : 0;
    return { lower, upper, digit, shift, other, pool, bits };
  };

  const feedback = (bits) => {
    if (bits >= 128) return 'The NSA is scared of you!';
    if (bits >= 100) return 'Practically uncrackable for centuries.';
    if (bits >= 89) return 'Good luck cracking that, H4x0r';
    if (bits >= 75) return 'Strong. Very hard to brute force.';
    if (bits >= 60) return 'Decent. Consider adding length.';
    if (bits >= 40) return 'Weak. Add symbols and length.';
    return 'Very weak. Use a longer passphrase.';
  };

  const update = () => {
    const pwd = input.value || '';
    const { lower, upper, digit, shift, other, pool, bits } = estimate(pwd);
    hasLower.textContent = lower ? '✓' : '✗';
    hasUpper.textContent = upper ? '✓' : '✗';
    hasDigit.textContent = digit ? '✓' : '✗';
    hasShift.textContent = shift ? '✓' : '✗';
    hasOther.textContent = other ? '✓' : '✗';
    poolTotal.textContent = String(pool);
    bitsOut.textContent = `~${Math.round(bits)} Bits`;
    resultTag.textContent = pwd ? feedback(bits) : 'Start typing to see the entropy score';
  };

  input.addEventListener('input', update);
  showPw?.addEventListener('change', () => { input.type = showPw.checked ? 'text' : 'password'; });
  clearPw?.addEventListener('click', () => { input.value=''; update(); });
  update();
})();


