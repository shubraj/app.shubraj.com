window.addEventListener('load', () => {
    const imageInput = document.getElementById('imageInput');
    const imageCanvas = document.getElementById('imageCanvas');
    const hexValue = document.getElementById('hexValue');
    const rgbValue = document.getElementById('rgbValue');
    const hslValue = document.getElementById('hslValue');
    const ctx = imageCanvas.getContext('2d');

    // Load the default image
    const defaultImage = new Image();
    defaultImage.src = imageInput.src;
    defaultImage.onload = function () {
        imageCanvas.width = defaultImage.width;
        imageCanvas.height = defaultImage.height;
        ctx.drawImage(defaultImage, 0, 0, imageCanvas.width, imageCanvas.height);
    };

    // Function to handle file uploads
    imageInput.addEventListener('change', function () {
        const file = imageInput.files[0];
        if (!file) return;

        const img = new Image();
        const reader = new FileReader();

        reader.onload = function (event) {
            img.src = event.target.result;
            img.onload = function () {
                // Set canvas size to the image size
                imageCanvas.width = img.width;
                imageCanvas.height = img.height;
                ctx.drawImage(img, 0, 0);
            };
        };
        reader.readAsDataURL(file);
    });

    // Detect click event on the canvas to get the color
    imageCanvas.addEventListener('click', function (event) {
        const rect = imageCanvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // Get pixel color at the clicked position
        const pixel = ctx.getImageData(x, y, 1, 1).data;
        const r = pixel[0], g = pixel[1], b = pixel[2];

        // Update RGB
        rgbValue.value = `rgb(${r}, ${g}, ${b})`;

        // Convert to HEX
        hexValue.value = `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`;

        // Convert to HSL
        const [h, s, l] = rgbToHsl(r, g, b);
        hslValue.value = `hsl(${h}, ${s}%, ${l}%)`;
    });

    // Helper function to convert RGB to HSL
    function rgbToHsl(r, g, b) {
        r /= 255, g /= 255, b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0; // achromatic
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h /= 6;
        }
        return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
    }
});