document.addEventListener('DOMContentLoaded', function () {
    const svgInput = document.getElementById('svgInput');
    const convertBtn = document.getElementById('convertSVGBtn');
    const downloadBtn = document.getElementById('downloadSVGBtn');

    // Enable the Convert button when a file is selected
    svgInput.addEventListener('change', function () {
        convertBtn.disabled = svgInput.files.length === 0;
        downloadBtn.disabled = true; 
    });

    // Convert SVG to JPG when Convert button is clicked
    convertBtn.addEventListener('click', function () {
        const file = svgInput.files[0];

        if (file && file.type === 'image/svg+xml') {
            const reader = new FileReader();

            reader.onload = function (e) {
                const svgData = e.target.result;

                // Create an offscreen canvas to draw the SVG
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const img = new Image();

                img.onload = function () {
                    // Set canvas dimensions to match the SVG dimensions
                    canvas.width = img.width;
                    canvas.height = img.height;

                    // Fill the canvas with a white background
                    ctx.fillStyle = 'white';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // Draw the SVG image onto the canvas
                    ctx.drawImage(img, 0, 0);

                    // Convert canvas content to JPG data URL
                    const jpgDataUrl = canvas.toDataURL('image/jpeg');
                    const originalFileName = file.name.split('.').slice(0, -1).join('.') + '.jpg';

                    // Create a download link for the JPG
                    downloadBtn.href = jpgDataUrl;
                    downloadBtn.download = originalFileName;
                    downloadBtn.disabled = false;  // Enable download button
                };

                img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgData);
            };

            reader.readAsText(file);
        } else {
            alert("Please upload a valid SVG file.");
        }
    });

    downloadBtn.addEventListener('click', function () {
        const link = document.createElement('a');
        link.href = downloadBtn.href;
        link.download = downloadBtn.download;
        link.click();
    });
});
