const emailInput = document.getElementById('emailInput');
const statusOutput = document.getElementById('emailOutput');
const verifyBtn = document.getElementById('verifyBtn');
const emailForm = document.getElementById('emailForm');

// Enable verify button only if email format is valid
emailInput.addEventListener('input', () => {
    verifyBtn.disabled = !isValidEmail(emailInput.value.trim());
});
