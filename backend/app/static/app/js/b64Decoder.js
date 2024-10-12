const textInput = document.getElementById('textInput');
const textOutput = document.getElementById('textOutput');
const clearBtn = document.getElementById('clearBtn');

// Enable clear button when there's input
textInput.addEventListener('input', () => {
    if (textInput.value.trim() !== '') {
        clearBtn.disabled = false;  // Enable clear button when there's input
        try {
            const decodedText = atob(textInput.value);
            textOutput.value = decodedText;
        } catch (error) {
            textOutput.value = 'Error decoding the Base64 text!';
        }
    } else {
        textOutput.value = '';  // Clear output when input is empty
        clearBtn.disabled = true;  // Disable clear button when input is empty
    }
});

// Clear Input and Output
clearBtn.addEventListener('click', () => {
    textInput.value = '';
    textOutput.value = '';
    clearBtn.disabled = true;  // Disable clear button after clearing
});