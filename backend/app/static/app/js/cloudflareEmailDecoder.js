document.addEventListener('DOMContentLoaded', function () {
    const obfuscatedInput = document.getElementById('obfuscatedInput');
    const decodeBtn = document.getElementById('decodeBtn');
    const decodedOutput = document.getElementById('decodedOutput');

    // Enable the Decode button when input is provided
    obfuscatedInput.addEventListener('input', function () {
        decodeBtn.disabled = obfuscatedInput.value.trim() === '';
    });

    // Decode the obfuscated email when the button is clicked
    decodeBtn.addEventListener('click', function () {
        const obfuscatedEmail = obfuscatedInput.value.trim();
        const decodedEmail = deobfuscateProtectedEmail(obfuscatedEmail);
        decodedOutput.value = decodedEmail; // Show decoded email in output
    });

    // Function to deobfuscate the email
    function deobfuscateProtectedEmail(obfuscatedEmail) {
        const XOR_key = parseInt(obfuscatedEmail.slice(0, 2), 16);
        let email = '';
        for (let i = 2; i < obfuscatedEmail.length; i += 2) {
            email += String.fromCharCode(parseInt(obfuscatedEmail.slice(i, i + 2), 16) ^ XOR_key);
        }
        return email;
    }
});
