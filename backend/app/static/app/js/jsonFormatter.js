const formatBtn = document.getElementById('formatBtn');
const clearBtn = document.getElementById('clearBtn');
const jsonInput = document.getElementById('jsonInput');
const jsonOutput = document.getElementById('jsonOutput');

// Format JSON
formatBtn.addEventListener('click', () => {
    try {
        const formattedJson = JSON.stringify(JSON.parse(jsonInput.value), null, 4);
        jsonOutput.value = formattedJson;
    } catch (error) {
        jsonOutput.value = 'Invalid JSON format!';
    }
});

// Clear Input and Output
clearBtn.addEventListener('click', () => {
    jsonInput.value = '';
    jsonOutput.value = '';
});