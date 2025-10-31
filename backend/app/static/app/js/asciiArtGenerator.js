// ASCII Art Generator
(function() {
    'use strict';
    
    const textInput = document.getElementById('asciiTextInput');
    const outputText = document.getElementById('asciiOutput');
    const fontSelect = document.getElementById('asciiFont');
    const copyBtn = document.getElementById('asciiCopyBtn');
    const clearBtn = document.getElementById('asciiClearBtn');
    const showBtn = document.getElementById('asciiShowBtn');
    
    if (!textInput || !outputText) return;
    
    // ASCII art fonts using Figlet-style characters
    const fonts = {
        standard: {
            name: 'Standard',
            chars: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !@#$%^&*()_+-=[]{}|;:,.<>?'
        },
        block: {
            name: 'Block',
            mapping: {
                'A': ' ████ \n██  ██\n██████\n██  ██\n██  ██\n',
                'B': '█████ \n██  ██\n█████ \n██  ██\n█████ \n',
                // Simplified block style
            }
        }
    };
    
    // Simple ASCII art mapping (expanded basic set)
    const charMap = {
        'A': '    /\\    \n   /  \\   \n  /----\\  \n /      \\ \n/        \\\n',
        'B': '|-----|  \n|      |  \n|-----|  \n|      |  \n|-----|  \n',
        'C': '  .----  \n /     / \n|      | \n \\     / \n  `---` \n',
        'D': '|-----|  \n|      | \n|      | \n|      | \n|-----|  \n',
        'E': '|------ \n|       \n|----   \n|       \n|------ \n',
        'F': '|------ \n|       \n|----   \n|       \n|       \n',
        'G': '  .----  \n /     / \n|   --| \n \\     \\\n  `----`\n',
        'H': '|     | \n|     | \n|-----| \n|     | \n|     | \n',
        'I': '  ---  \n   |   \n   |   \n   |   \n   |   \n  ---  \n',
        'J': '     | \n     | \n     | \n|    | \n `--`  \n',
        'K': '|   / \n|  /  \n|--   \n|  \\  \n|   \\ \n',
        'L': '|      \n|      \n|      \n|      \n|----- \n',
        'M': '|\\    /|\n| \\  / |\n|  \\/  |\n|      |\n|      |\n',
        'N': '|\\    |\n| \\   |\n|  \\  |\n|   \\ |\n|    \\|\n',
        'O': ' .---- \n/     \\\n|     |\n\\     /\n `---` \n',
        'P': '|----  \n|    | \n|----  \n|      \n|      \n',
        'Q': ' .---- \n/     \\\n|     |\n\\  \\  /\n `--` \\\n',
        'R': '|----  \n|    | \n|----  \n|   \\  \n|    \\ \n',
        'S': ' .---- \n/      \n `---- \n      \\\n `----` \n',
        'T': '-------\n   |   \n   |   \n   |   \n   |   \n',
        'U': '|     |\n|     |\n|     |\n|     |\n `---` \n',
        'V': '\\     /\n \\   / \n  \\ /  \n   V   \n',
        'W': '|     |\n|  |  |\n|  |  |\n|\\/ \\/|\n|     |\n',
        'X': '\\   /\n \\ / \n  X  \n / \\ \n/   \\\n',
        'Y': '\\   /\n \\ / \n  |  \n  |  \n  |  \n',
        'Z': '------\n    / \n   /  \n  /   \n------\n',
        '0': ' .---- \n/     \\\n|     |\n\\     /\n `---` \n',
        '1': '   |   \n   |   \n   |   \n   |   \n   |   \n',
        '2': ' .---- \n     / \n .---- \n/      \n`----` \n',
        '3': ' .---- \n     / \n .---- \n     / \n`----` \n',
        '4': '|     |\n|-----|\n      |\n      |\n      |\n',
        '5': '|---- \n|     \n|---- \n     |\n`----`\n',
        '6': ' .---- \n/      \n|----  \n|    | \n `---` \n',
        '7': '------\n     /\n    / \n   /  \n  /   \n',
        '8': ' .---- \n/     \\\n|-----|\n|     |\n `---` \n',
        '9': ' .---- \n/     \\\n|-----|\n      /\n `---` \n',
        ' ': '     \n     \n     \n     \n     \n',
        '!': ' | \n | \n | \n   \n . \n',
        '?': ' .---- \n/     / \n      \\ \n   |   \n   .   \n',
        '.': '   \n   \n   \n   \n . \n',
        ',': '   \n   \n   \n . \n` \n',
        '-': '      \n      \n ---- \n      \n      \n',
        '_': '      \n      \n      \n      \n------\n',
        '@': ' .---- \n/  --  \\\n| (  ) |\n\\  --  /\n `----`\n',
        '#': '  #  # \n ######\n  #  # \n ######\n  #  # \n',
        '$': '  |    \n ----- \n  |    \n ----- \n  |    \n',
        '%': '#    /\n    /  \n   /   \n  /    \n/    #\n',
        '&': '  .--  \n /   \\ \n|  `-- \n \\   / \n  `--` \n',
        '*': '      \n  /\\  \n <  > \n  \\/  \n      \n      \n',
        '+': '      \n   |  \n --+--\n   |  \n      \n',
        '=': '      \n ----- \n      \n ----- \n      \n',
        '(': '  /  \n /   \n|    \n \\   \n  \\  \n',
        ')': '\\    \n \\   \n  |  \n /   \n/    \n',
        '[': '|--- \n|    \n|    \n|    \n|--- \n',
        ']': '---| \n    | \n    | \n    | \n---| \n',
        '{': '  /- \n /   \n|    \n \\   \n  \\- \n',
        '}': '-\\  \n  \\  \n   | \n  /  \n-/   \n',
        '|': '  |  \n  |  \n  |  \n  |  \n  |  \n',
        '/': '     / \n    /  \n   /   \n  /    \n /     \n',
        '\\': '\\     \n \\    \n  \\   \n   \\  \n    \\ \n',
        ':': '   \n . \n   \n . \n   \n',
        ';': '   \n . \n   \n . \n` \n',
        '<': '   /  \n  /   \n /    \n  \\   \n   \\  \n',
        '>': '\\    \n \\   \n  \\  \n /   \n/    \n',
    };
    
    // Fixed width for all characters (normalize to this width)
    const CHAR_WIDTH = 10;
    const CHAR_HEIGHT = 6;
    
    // Normalize a character's ASCII representation to fixed width and height
    function normalizeChar(asciiChar, targetHeight = CHAR_HEIGHT) {
        const lines = asciiChar.split('\n').filter(l => l !== '');
        const normalized = [];
        
        // Find the maximum width in the character to ensure proper alignment
        let maxWidth = 0;
        lines.forEach(line => {
            maxWidth = Math.max(maxWidth, line.length);
        });
        
        for (let i = 0; i < targetHeight; i++) {
            const line = i < lines.length ? lines[i] : '';
            // Pad to fixed width - ensure consistent alignment
            const padded = line.length >= CHAR_WIDTH 
                ? line.substring(0, CHAR_WIDTH) 
                : (line + ' '.repeat(CHAR_WIDTH - line.length));
            normalized.push(padded);
        }
        
        return normalized;
    }
    
    // Convert text to ASCII art
    function textToAscii(text, font = 'standard') {
        if (!text || text.trim() === '') return '';
        
        const inputLines = text.toUpperCase().split('\n');
        const output = [];
        
        inputLines.forEach((line) => {
            if (line.trim() === '') {
                // Add empty lines for spacing between text lines
                for (let i = 0; i < CHAR_HEIGHT; i++) {
                    output.push('');
                }
                return;
            }
            
            // Normalize each character to fixed dimensions
            const normalizedChars = [];
            for (let i = 0; i < line.length; i++) {
                const char = line[i];
                // Default empty character representation
                const defaultChar = ' '.repeat(CHAR_WIDTH) + '\n'.repeat(CHAR_HEIGHT - 1);
                const asciiChar = charMap[char] || defaultChar.replace(/\n/g, '\n' + ' '.repeat(CHAR_WIDTH));
                normalizedChars.push(normalizeChar(asciiChar, CHAR_HEIGHT));
            }
            
            // Combine characters row by row with consistent alignment
            for (let row = 0; row < CHAR_HEIGHT; row++) {
                let rowText = '';
                for (let i = 0; i < normalizedChars.length; i++) {
                    const charRow = normalizedChars[i][row] || ' '.repeat(CHAR_WIDTH);
                    rowText += charRow;
                }
                // Trim trailing spaces but keep structure
                output.push(rowText);
            }
        });
        
        return output.join('\n');
    }
    
    // Generate ASCII art
    function generateAscii() {
        const text = textInput.value.trim();
        if (!text) {
            outputText.value = '';
            copyBtn.disabled = true;
            return;
        }
        
        const selectedFont = fontSelect.value;
        const asciiArt = textToAscii(text, selectedFont);
        outputText.value = asciiArt;
        copyBtn.disabled = false;
    }
    
    // Event listeners
    if (textInput) {
        textInput.addEventListener('input', generateAscii);
        textInput.addEventListener('keyup', generateAscii);
    }
    
    if (fontSelect) {
        fontSelect.addEventListener('change', generateAscii);
    }
    
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            outputText.select();
            document.execCommand('copy');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        });
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            textInput.value = '';
            outputText.value = '';
            copyBtn.disabled = true;
            textInput.focus();
        });
    }
    
    if (showBtn) {
        showBtn.addEventListener('click', () => {
            const previewContent = document.getElementById('asciiPreviewContent');
            const previewDiv = document.getElementById('asciiPreview');
            if (previewContent && previewDiv && outputText.value) {
                previewContent.textContent = outputText.value;
                previewDiv.style.display = 'block';
            }
        });
    }
    
    // Initialize
    if (textInput.value) {
        generateAscii();
    }
})();

