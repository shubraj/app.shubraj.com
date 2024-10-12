document.addEventListener('DOMContentLoaded', function () {
    const hexInput = document.getElementById('hexInput');
    const rgbInput = document.getElementById('rgbInput');
    const hslInput = document.getElementById('hslInput');
    const convertBtn = document.getElementById('convertBtn');

    // Enable the Convert button when a file is selected
    hexInput.addEventListener('input', toggleConvertButton);
    rgbInput.addEventListener('input', toggleConvertButton);
    hslInput.addEventListener('input', toggleConvertButton);

    function toggleConvertButton() {
        convertBtn.disabled = !(hexInput.value || rgbInput.value || hslInput.value);
    }

    // Convert HEX to RGB
    function hexToRgb(hex) {
        // Expand short hex to full hex
        if (hex.length === 4) {
            hex = `#${hex[1]}${hex[1]}${hex[2]}${hex[2]}${hex[3]}${hex[3]}`;
        }
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgb(${r}, ${g}, ${b})`;
    }

    // Convert RGB to HSL
    function rgbToHsl(rgb) {
        const rgbValues = rgb.match(/\d+/g).map(Number);
        const [r, g, b] = rgbValues.map(value => value / 255);
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0; // achromatic
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - (max + min)) : d / (max + min);
            switch (max) {
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h /= 6; // Normalize h to [0, 1]
        }

        return `hsl(${Math.round(h * 360)}, ${Math.round(s * 100)}%, ${Math.round(l * 100)}%)`;
    }

    // Convert HSL to RGB
    function hslToRgb(hsl) {
        const hslValues = hsl.match(/\d+/g).map(Number);
        let [h, s, l] = hslValues;
        h /= 360; s /= 100; l /= 100;

        let r, g, b;
        if (s === 0) {
            r = g = b = l; // achromatic
        } else {
            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hueToRgb(p, q, h + 1 / 3);
            g = hueToRgb(p, q, h);
            b = hueToRgb(p, q, h - 1 / 3);
        }

        return `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`;
    }

    // Helper function to convert hue to RGB
    function hueToRgb(p, q, h) {
        if (h < 0) h += 1;
        if (h > 1) h -= 1;
        if (h < 1 / 6) return p + (q - p) * 6 * h;
        if (h < 1 / 2) return q;
        if (h < 2 / 3) return p + (q - p) * (2 / 3 - h) * 6;
        return p;
    }

    // Convert color codes when the button is clicked
    convertBtn.addEventListener('click', function () {
        const hex = hexInput.value.trim();
        const rgb = rgbInput.value.trim();
        const hsl = hslInput.value.trim();

        if (hex) {
            // Convert HEX to RGB and HSL
            const rgbValue = hexToRgb(hex);
            const hslValue = rgbToHsl(rgbValue);
            rgbInput.value = rgbValue;
            hslInput.value = hslValue;
        } else if (rgb) {
            // Convert RGB to HEX and HSL
            const hexValue = '#' + rgb.match(/\d+/g).map((v) => {
                const hex = parseInt(v).toString(16).padStart(2, '0');
                return hex;
            }).join('');
            const hslValue = rgbToHsl(rgb);
            hexInput.value = hexValue;
            hslInput.value = hslValue;
        } else if (hsl) {
            // Convert HSL to RGB and HEX
            const rgbValue = hslToRgb(hsl);
            const hexValue = '#' + rgbValue.match(/\d+/g).map((v) => {
                const hex = parseInt(v).toString(16).padStart(2, '0');
                return hex;
            }).join('');
            hexInput.value = hexValue;
            rgbInput.value = rgbValue;
        }
    });
});
