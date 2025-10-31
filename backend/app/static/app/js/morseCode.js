// Morse Code Dictionary
const morseCodeDict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--',
    '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...',
    ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
    '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'  // Space between words
};

// Reverse dictionary for decoding
const reverseMorseDict = {};
Object.keys(morseCodeDict).forEach(key => {
    reverseMorseDict[morseCodeDict[key]] = key;
});

function encodeToMorse(text) {
    if (!text || text.trim() === '') return '';
    
    const upperText = text.toUpperCase();
    const result = [];
    
    for (let i = 0; i < upperText.length; i++) {
        const char = upperText[i];
        if (morseCodeDict[char] !== undefined) {
            result.push(morseCodeDict[char]);
        } else if (char === ' ') {
            // Space between words
            result.push('/');
        } else {
            // Unknown character - keep as is or skip
            // Optionally: result.push('?');
        }
    }
    
    return result.join(' ');
}

function decodeFromMorse(morse) {
    if (!morse || morse.trim() === '') return '';
    
    // Normalize spacing: replace multiple spaces with single space
    const normalizedMorse = morse.replace(/\s+/g, ' ').trim();
    
    // Split by spaces or slashes (word separators)
    const words = normalizedMorse.split(' / ');
    const result = [];
    
    for (const word of words) {
        const letters = word.trim().split(' ');
        const decodedWord = [];
        
        for (const letter of letters) {
            if (letter === '') continue;
            
            if (reverseMorseDict[letter] !== undefined) {
                decodedWord.push(reverseMorseDict[letter]);
            } else {
                // Unknown morse code - keep as is or add marker
                decodedWord.push('?');
            }
        }
        
        result.push(decodedWord.join(''));
    }
    
    return result.join(' ');
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const textInput = document.getElementById('morseTextInput');
    const morseInput = document.getElementById('morseCodeInput');
    const encodeBtn = document.getElementById('morseEncodeBtn');
    const decodeBtn = document.getElementById('morseDecodeBtn');
    const copyMorseBtn = document.getElementById('copyMorseBtn');
    const copyTextBtn = document.getElementById('copyTextBtn');
    const clearBtn = document.getElementById('morseClearBtn');
    const playMorseBtn = document.getElementById('playMorseBtn');
    
    if (encodeBtn) {
        encodeBtn.addEventListener('click', function() {
            const text = textInput.value;
            const morse = encodeToMorse(text);
            morseInput.value = morse;
            
            // Enable copy button
            if (copyMorseBtn) copyMorseBtn.disabled = false;
            if (playMorseBtn) playMorseBtn.disabled = !morse;
        });
    }
    
    if (decodeBtn) {
        decodeBtn.addEventListener('click', function() {
            const morse = morseInput.value;
            const text = decodeFromMorse(morse);
            textInput.value = text;
            
            // Enable copy button
            if (copyTextBtn) copyTextBtn.disabled = false;
        });
    }
    
    if (copyMorseBtn) {
        copyMorseBtn.addEventListener('click', function() {
            morseInput.select();
            document.execCommand('copy');
            
            // Visual feedback
            const originalText = copyMorseBtn.textContent;
            copyMorseBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyMorseBtn.textContent = originalText;
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
            morseInput.value = '';
            textInput.focus();
            
            // Disable copy buttons
            if (copyMorseBtn) copyMorseBtn.disabled = true;
            if (copyTextBtn) copyTextBtn.disabled = true;
            if (playMorseBtn) playMorseBtn.disabled = true;
        });
    }
    
    if (playMorseBtn) {
        playMorseBtn.addEventListener('click', function() {
            const morse = morseInput.value;
            if (morse) {
                playMorseCode(morse);
            }
        });
    }
});

function playMorseCode(morse) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const dotDuration = 0.1; // seconds
    const dashDuration = 0.3; // seconds
    const elementPause = 0.1; // pause between elements
    const letterPause = 0.3; // pause between letters
    const wordPause = 0.7; // pause between words
    
    const frequency = 600; // Hz
    
    let currentTime = audioContext.currentTime;
    
    for (let i = 0; i < morse.length; i++) {
        const char = morse[i];
        
        if (char === '.') {
            // Play dot
            playTone(audioContext, frequency, currentTime, dotDuration);
            currentTime += dotDuration + elementPause;
        } else if (char === '-') {
            // Play dash
            playTone(audioContext, frequency, currentTime, dashDuration);
            currentTime += dashDuration + elementPause;
        } else if (char === ' ') {
            // Pause between letters
            currentTime += letterPause;
        } else if (char === '/') {
            // Pause between words
            currentTime += wordPause;
        }
    }
}

function playTone(audioContext, frequency, startTime, duration) {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = frequency;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, startTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + duration);
    
    oscillator.start(startTime);
    oscillator.stop(startTime + duration);
}

