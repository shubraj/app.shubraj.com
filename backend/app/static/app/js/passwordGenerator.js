const lengthRange = document.getElementById('lengthRange');
const lengthValue = document.getElementById('lengthValue');
const passwordOutput = document.getElementById('passwordOutput');
const regenerateBtn = document.getElementById('regenerateBtn');
const copyBtn = document.getElementById('copyBtn');
const toast = document.getElementById('toast');
const uppercase = document.getElementById('uppercase');
const lowercase = document.getElementById('lowercase');
const numbers = document.getElementById('numbers');
const symbols = document.getElementById('symbols');

// Character sets
const charSets = {
    uppercase: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    lowercase: "abcdefghijklmnopqrstuvwxyz",
    numbers: "0123456789",
    symbols: "!@#$%^&*()_+[]{}|;:,.<>?",
};

// Update the displayed length
lengthRange.addEventListener('input', function() {
    lengthValue.textContent = lengthRange.value;
    generatePassword();
});

// Generate password
function generatePassword() {
    let charset = "";
    if (uppercase.checked) charset += charSets.uppercase;
    if (lowercase.checked) charset += charSets.lowercase;
    if (numbers.checked) charset += charSets.numbers;
    if (symbols.checked) charset += charSets.symbols;

    let password = "";
    for (let i = 0; i < lengthRange.value; i++) {
        let char = charset.charAt(Math.floor(Math.random() * charset.length));
        password += char;
    }

    passwordOutput.textContent = password || "Customize your password";
}

// Automatically generate a password when any parameter changes
document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', generatePassword);
});

// Regenerate the password when the regenerate button is clicked
regenerateBtn.addEventListener('click', generatePassword);

// Copy password to clipboard with toast notification
copyBtn.addEventListener('click', function() {
    navigator.clipboard.writeText(passwordOutput.textContent).then(() => {
        // Show toast notification
        toast.className = "toast show";
        setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
    });
});

// Generate an initial password when the page loads
window.onload = generatePassword;