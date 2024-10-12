const textInput = document.getElementById('textInput');
const textOutput = document.getElementById('textOutput');
const clearBtn = document.getElementById('clearBtn');

// Base64 Encode as the user types
textInput.addEventListener('input', () => {
    if (textInput.value.trim())
    {
        clearBtn.disabled = false;
    } else {
        clearBtn.disabled = true;
    }
    try {
        const encodedText = btoa(textInput.value);
        textOutput.value = encodedText;
    } catch (error) {
        textOutput.value = 'Error encoding the text!';
    }
});

// Clear Input and Output
clearBtn.addEventListener('click', () => {
    textInput.value = '';
    textOutput.value = '';
});
