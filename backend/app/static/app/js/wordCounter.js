const textInput = document.getElementById('textInput');
const wordCountDisplay = document.getElementById('wordCount');
const charCountDisplay = document.getElementById('charCount');
const charCountNoSpacesDisplay = document.getElementById('charCountNoSpaces');
const sentenceCountDisplay = document.getElementById('sentenceCount');

// Function to update counts
function updateCounts() {
    const text = textInput.value;

    // Word Count
    const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;

    // Character Count
    const charCount = text.length;

    // Character Count (excluding spaces)
    const charCountNoSpaces = text.replace(/\s/g, '').length;

    // Sentence Count
    const sentenceCount = text.split(/[.!?]+/).filter(Boolean).length;

    // Update Display
    wordCountDisplay.textContent = `Words: ${wordCount}`;
    charCountDisplay.textContent = `Characters: ${charCount}`;
    charCountNoSpacesDisplay.textContent = `Characters (no spaces): ${charCountNoSpaces}`;
    sentenceCountDisplay.textContent = `Sentences: ${sentenceCount}`;
}

// Add event listener for real-time updates
textInput.addEventListener('input', updateCounts);