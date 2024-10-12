const bcrypt = dcodeIO.bcrypt;
const textInput = document.getElementById('hashInput');
const bcryptOutput = document.getElementById('hashOutput');
const saltRounds = document.getElementById('hashVersion');
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

// Generate Bcrypt hash
generateBtn.addEventListener('click', async function() {
    const text = textInput.value.trim();
    const rounds = parseInt(saltRounds.value, 10);

    if (!text || isNaN(rounds) || rounds < 4 || rounds > 20) {
        alert("Please enter valid text and choose salt rounds between 4 and 20.");
        return;
    }

    const hash = await bcrypt.hash(text, rounds);
    bcryptOutput.textContent = hash;
    outputCard.style.display = 'block';  // Show the output card
    copyBtn.disabled = false;  // Enable copy button after hash generation
});

// Copy Bcrypt hash to clipboard
copyBtn.addEventListener('click', function() {
    const hash = bcryptOutput.textContent;
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