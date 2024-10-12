function beautifyCSS(css) {
    // Remove all existing whitespace
    css = css.replace(/\s+/g, ' ').trim();

    // Helper function to format selectors
    function formatSelectors(selectors) {
        return selectors.split(',').map(s => s.trim()).join(',\n');
    }

    // Helper function to format properties
    function formatProperties(properties) {
        return properties.split(';').map(p => {
            let [name, value] = p.split(':').map(s => s.trim());
            return name && value ? `  ${name}: ${value};` : '';
        }).filter(Boolean).join('\n');
    }

    let formatted = '';
    let depth = 0;
    let inComment = false;
    let buffer = '';

    for (let i = 0; i < css.length; i++) {
        let char = css[i];
        let nextChar = css[i + 1] || '';

        // Handle comments
        if (char === '/' && nextChar === '*' && !inComment) {
            inComment = true;
            formatted += '\n' + '  '.repeat(depth) + '/*';
            i++;
            continue;
        }
        if (char === '*' && nextChar === '/' && inComment) {
            inComment = false;
            formatted += '*/\n';
            i++;
            continue;
        }
        if (inComment) {
            formatted += char;
            continue;
        }

        // Handle selectors and rules
        if (char === '{') {
            let selectors = formatSelectors(buffer);
            formatted += selectors + ' {\n';
            depth++;
            buffer = '';
        } else if (char === '}') {
            if (buffer.trim()) {
                formatted += formatProperties(buffer) + '\n';
            }
            depth = Math.max(0, depth - 1);
            formatted += '  '.repeat(depth) + '}\n\n';
            buffer = '';
        } else {
            buffer += char;
        }
    }

    // Add any remaining buffer
    if (buffer.trim()) {
        formatted += buffer;
    }

    return formatted.trim();
}

// Event listeners
document.getElementById('beautifyBtn').addEventListener('click', function() {
    const input = document.getElementById('cssInput').value;
    const beautified = beautifyCSS(input);
    document.getElementById('cssOutput').value = beautified;
});

document.getElementById('clearBtn').addEventListener('click', function() {
    document.getElementById('cssInput').value = '';
    document.getElementById('cssOutput').value = '';
});