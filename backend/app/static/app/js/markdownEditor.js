// Initialize the Markdown editor
const markdownInput = document.getElementById('markdownInput');
const markdownPreview = document.getElementById('markdownPreview');

// Function to update preview in real-time
function updatePreview() {
    const markdownText = markdownInput.value;
    markdownPreview.innerHTML = marked.parse(markdownText);
}

// Update the preview when typing
markdownInput.addEventListener('input', updatePreview);

// Set default markdown content
markdownInput.value = "# Welcome to Shub Raj App's Markdown Editor\n\nType your markdown on the left, and see the live preview on the right!";
updatePreview(); // Render initial content