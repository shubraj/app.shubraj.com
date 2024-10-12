const hashInput = document.getElementById('hashInput');
const hashOutput = document.getElementById('hashOutput');
const hashVersion = document.getElementById('hashVersion');
const generateBtn = document.getElementById('generateBtn');
const copyBtn = document.getElementById('copyBtn');
const outputCard = document.getElementById('hashCard');
const toast = document.getElementById('toast');

// Disable generate button initially
generateBtn.disabled = true;

// Enable generate button when text is entered
hashInput.addEventListener('input', function() {
    if (hashInput.value.trim() !== '') {
        generateBtn.disabled = false;  // Enable button when there's text
    } else {
        generateBtn.disabled = true;  // Disable button when input is empty
    }
});

// Generate SHA hash based on selected version
generateBtn.addEventListener('click', function() {
    const text = hashInput.value.trim();
    const selectedVersion = hashVersion.value;

    if (!text) {
        alert("Please enter some text.");
        return;
    }

    let hash;
    if (selectedVersion === 'SHA1') {
        hash = CryptoJS.SHA1(text).toString();
    } else if (selectedVersion === 'SHA224') {
        hash = CryptoJS.SHA224(text).toString();
    } else if (selectedVersion === 'SHA256') {
        hash = CryptoJS.SHA256(text).toString();
    } else if (selectedVersion === 'SHA384') {
        hash = CryptoJS.SHA384(text).toString();
    } else if (selectedVersion === 'SHA512') {
        hash = CryptoJS.SHA512(text).toString();
    }

    hashOutput.textContent = hash;
    outputCard.style.display = 'block';  // Show the output card
    copyBtn.disabled = false;  // Enable copy button after hash generation
});

// Copy SHA hash to clipboard
copyBtn.addEventListener('click', function() {
    const hash = hashOutput.textContent;
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