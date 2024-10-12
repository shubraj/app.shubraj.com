const textInput = document.getElementById('hashInput');
const md5Output = document.getElementById('hashOutput');
const generateBtn = document.getElementById('generateBtn');
const copyBtn = document.getElementById('copyBtn');
const outputCard = document.getElementById('hashCard');
const toast = document.getElementById('toast');

// Disable generate button initially
generateBtn.disabled = true;

// Enable generate button when text is entered
textInput.addEventListener('input', function() {
    if (textInput.value.trim() !== '') {
        generateBtn.disabled = false;  // Enable button when there's text
    } else {
        generateBtn.disabled = true;  // Disable button when input is empty
    }
});

// Generate MD5 hash
generateBtn.addEventListener('click', function() {
    const text = textInput.value.trim();
    if (!text) {
        alert("Please enter some text.");
        return;
    }

    const hash = CryptoJS.MD5(text).toString();
    md5Output.textContent = hash;
    outputCard.style.display = 'block';  // Show the output card
    copyBtn.disabled = false;  // Enable copy button after hash generation
});

// Copy MD5 hash to clipboard
copyBtn.addEventListener('click', function() {
    const hash = md5Output.textContent;
    if (!hash) {
        alert("No hash generated to copy.");
        return;
    }

    navigator.clipboard.writeText(hash).then(() => {
        // Show toast notification
        toast.classList.add('show');
        setTimeout(() => { toast.classList.remove('show'); }, 3000);
    });
});
