
const emailInput = document.getElementById('emailInput');
const statusOutput = document.getElementById('emailOutput');
const verifyBtn = document.getElementById('verifyBtn');

// Enable verify button when email is entered
emailInput.addEventListener('input', () => {
    if (emailInput.value.trim()){
        verifyBtn.disabled = false;
    } else {
        verifyBtn.disabled = true;
    }
});

// Email validation regex
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Simple regex for email validation
    return re.test(email);
}

// Simulate email verification API call
verifyBtn.addEventListener('click', () => {
    const email = emailInput.value.trim();

    // Simulating API call to verify email existence
    setTimeout(() => {
        let resultMessage;
        let resultColor;

        if (!isValidEmail(email)) {
            resultMessage = 'Invalid email format!';
            resultColor = 'yellow';
        } else {
            const isValid = Math.random() < 0.5;
            const mailboxExists = Math.random() < 0.5;

            if (isValid && mailboxExists) {
                resultMessage = `The email address "${email}" is valid and exists.`;
                resultColor = 'green';
            } else if (isValid && !mailboxExists) {
                resultMessage = `The email address "${email}" is valid but the mailbox doesn't exist.`;
                resultColor = 'blue';
            } else {
                resultMessage = `The email address "${email}" is valid but does not exist.`;
                resultColor = 'red';
            }
        }

        // Display the result
        statusOutput.style.display = 'block';
        statusOutput.textContent = resultMessage;
        statusOutput.style.backgroundColor = resultColor;
    }, 1000);
});