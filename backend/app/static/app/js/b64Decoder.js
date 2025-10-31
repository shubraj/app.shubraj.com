document.addEventListener('DOMContentLoaded', function() {
    const textInput = document.getElementById('textInput');
    const textOutput = document.getElementById('textOutput');
    const clearBtn = document.getElementById('clearBtn');
    const copyInputBtn = document.getElementById('copyInputBtn');
    const copyOutputBtn = document.getElementById('copyOutputBtn');

    // Enable/disable buttons and decode as user types
    textInput.addEventListener('input', () => {
        const hasInput = textInput.value.trim() !== '';
        
        if (hasInput) {
            clearBtn.disabled = false;
            copyInputBtn.disabled = false;
            
            try {
                const decodedText = atob(textInput.value);
                textOutput.value = decodedText;
                copyOutputBtn.disabled = false;
            } catch (error) {
                textOutput.value = 'Error decoding the Base64 text!';
                copyOutputBtn.disabled = true;
            }
        } else {
            textOutput.value = '';
            clearBtn.disabled = true;
            copyInputBtn.disabled = true;
            copyOutputBtn.disabled = true;
        }
    });

    // Clear Input and Output
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            textInput.value = '';
            textOutput.value = '';
            textInput.focus();
            
            clearBtn.disabled = true;
            if (copyInputBtn) copyInputBtn.disabled = true;
            if (copyOutputBtn) copyOutputBtn.disabled = true;
        });
    }

    // Copy Base64 input
    if (copyInputBtn) {
        copyInputBtn.addEventListener('click', function() {
            textInput.select();
            document.execCommand('copy');
            
            // Visual feedback
            const originalText = copyInputBtn.textContent;
            copyInputBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyInputBtn.textContent = originalText;
            }, 1000);
        });
    }

    // Copy decoded output
    if (copyOutputBtn) {
        copyOutputBtn.addEventListener('click', function() {
            textOutput.select();
            document.execCommand('copy');
            
            // Visual feedback
            const originalText = copyOutputBtn.textContent;
            copyOutputBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyOutputBtn.textContent = originalText;
            }, 1000);
        });
    }
});