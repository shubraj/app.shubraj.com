// Leet Speak Dictionary - mapping letters to leet equivalents
const leetDict = {
    'A': ['4', '@'],
    'B': ['8', '|3'],
    'C': ['<', '{', '['],
    'D': ['|)', '|]'],
    'E': ['3'],
    'F': ['|=', 'ph'],
    'G': ['6', '9'],
    'H': ['#', '/-/', '[-]'],
    'I': ['1', '!', '|'],
    'J': ['_|', '_/', ']'],
    'K': ['|<', '|<', '|{'],
    'L': ['1', '|', '|_'],
    'M': ['|\\/|', '|\'|\'|', '(\\/)', '/\\/\\'],
    'N': ['|\\|', '/\\/', '{\\}'],
    'O': ['0', '()', '[]'],
    'P': ['|*', '|o', '|>'],
    'Q': ['0_', '(,)', 'kw'],
    'R': ['|2', '|?', 'l2'],
    'S': ['5', '$', 'z'],
    'T': ['7', '+', '|-|'],
    'U': ['|_|', '(_)', '\\/'],
    'V': ['\\/', '|/', '\\|'],
    'W': ['\\/\\/', '\\X/', '(/\\)', '\\|/'],
    'X': ['><', '}{', ')('],
    'Y': ['`/', '`(', '`/'],
    'Z': ['2', '7_', '>_'],
    '0': ['O', '()'],
    '1': ['l', 'I', '|'],
    '2': ['Z', 'z'],
    '3': ['E', 'e'],
    '4': ['A', 'a'],
    '5': ['S', 's'],
    '6': ['G', 'g'],
    '7': ['T', 't'],
    '8': ['B', 'b'],
    '9': ['g', 'G']
};

// Reverse mapping for decoding (most common patterns)
const reverseLeetDict = {
    '4': 'A', '@': 'A',
    '8': 'B', '|3': 'B',
    '<': 'C', '{': 'C', '[': 'C',
    '|)': 'D', '|]': 'D',
    '3': 'E',
    '|=': 'F', 'ph': 'F',
    '6': 'G', '9': 'G',
    '#': 'H', '/-/': 'H',
    '1': 'I', '!': 'I', '|': 'I',
    '_|': 'J', '_/': 'J', ']': 'J',
    '|<': 'K', '|{': 'K',
    '1': 'L', '|_': 'L',
    '|\\/|': 'M', '(\\/)': 'M', '/\\/\\': 'M',
    '|\\|': 'N', '/\\/': 'N',
    '0': 'O', '()': 'O', '[]': 'O',
    '|*': 'P', '|o': 'P', '|>': 'P',
    '0_': 'Q', '(,)': 'Q',
    '|2': 'R', 'l2': 'R',
    '5': 'S', '$': 'S', 'z': 'S',
    '7': 'T', '+': 'T', '|-|': 'T',
    '|_|': 'U', '(_)': 'U', '\\/': 'U',
    '\\/': 'V', '|/': 'V', '\\|': 'V',
    '\\/\\/': 'W', '(/\\)': 'W', '\\|/': 'W',
    '><': 'X', '}{': 'X', ')(': 'X',
    '`/': 'Y', '`(': 'Y',
    '2': 'Z', '7_': 'Z', '>_': 'Z'
};

function encodeToLeet(text, level = 'medium') {
    if (!text || text.trim() === '') return '';
    
    const upperText = text.toUpperCase();
    let result = '';
    
    for (let i = 0; i < upperText.length; i++) {
        const char = upperText[i];
        
        if (leetDict[char]) {
            const replacements = leetDict[char];
            
            if (level === 'low') {
                // Low: use first replacement, sometimes keep original
                result += Math.random() > 0.5 ? replacements[0] : char;
            } else if (level === 'medium') {
                // Medium: use random replacement from first 2 if available
                const choice = replacements.length > 1 
                    ? replacements[Math.floor(Math.random() * Math.min(2, replacements.length))]
                    : replacements[0];
                result += choice;
            } else if (level === 'high') {
                // High: use random replacement from all options
                const choice = replacements[Math.floor(Math.random() * replacements.length)];
                result += choice;
            } else {
                // Extreme: maximum leet
                const choice = replacements[replacements.length - 1] || replacements[0];
                result += choice;
            }
        } else {
            // Keep non-leetable characters as-is
            result += char;
        }
    }
    
    return result;
}

function decodeFromLeet(leetText) {
    if (!leetText || leetText.trim() === '') return '';
    
    let result = '';
    let i = 0;
    
    while (i < leetText.length) {
        let found = false;
        
        // Try to match multi-character leet codes first (longest match)
        for (let len = 4; len >= 1 && !found; len--) {
            if (i + len <= leetText.length) {
                const substr = leetText.substring(i, i + len);
                
                if (reverseLeetDict[substr]) {
                    result += reverseLeetDict[substr];
                    i += len;
                    found = true;
                }
            }
        }
        
        // If no leet code found, keep original character
        if (!found) {
            result += leetText[i];
            i++;
        }
    }
    
    return result;
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const textInput = document.getElementById('leetTextInput');
    const leetInput = document.getElementById('leetSpeakInput');
    const levelSelect = document.getElementById('leetLevel');
    const encodeBtn = document.getElementById('leetEncodeBtn');
    const decodeBtn = document.getElementById('leetDecodeBtn');
    const copyLeetBtn = document.getElementById('copyLeetBtn');
    const copyTextBtn = document.getElementById('copyTextBtn');
    const clearBtn = document.getElementById('leetClearBtn');
    
    if (encodeBtn) {
        encodeBtn.addEventListener('click', function() {
            const text = textInput.value;
            const level = levelSelect ? levelSelect.value : 'medium';
            const leet = encodeToLeet(text, level);
            leetInput.value = leet;
            
            // Enable copy button
            if (copyLeetBtn) copyLeetBtn.disabled = false;
        });
    }
    
    if (decodeBtn) {
        decodeBtn.addEventListener('click', function() {
            const leet = leetInput.value;
            const text = decodeFromLeet(leet);
            textInput.value = text;
            
            // Enable copy button
            if (copyTextBtn) copyTextBtn.disabled = false;
        });
    }
    
    if (copyLeetBtn) {
        copyLeetBtn.addEventListener('click', function() {
            leetInput.select();
            document.execCommand('copy');
            
            // Visual feedback
            const originalText = copyLeetBtn.textContent;
            copyLeetBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyLeetBtn.textContent = originalText;
            }, 1000);
        });
    }
    
    if (copyTextBtn) {
        copyTextBtn.addEventListener('click', function() {
            textInput.select();
            document.execCommand('copy');
            
            // Visual feedback
            const originalText = copyTextBtn.textContent;
            copyTextBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyTextBtn.textContent = originalText;
            }, 1000);
        });
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            textInput.value = '';
            leetInput.value = '';
            textInput.focus();
            
            // Disable copy buttons
            if (copyLeetBtn) copyLeetBtn.disabled = true;
            if (copyTextBtn) copyTextBtn.disabled = true;
        });
    }
});

