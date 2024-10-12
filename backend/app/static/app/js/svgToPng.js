document.addEventListener('DOMContentLoaded', function () {
    const svgInput = document.getElementById('svgInput');
    const convertBtn = document.getElementById('convertSVGBtn');
    const downloadBtn = document.getElementById('downloadSVGBtn');

    // Enable the Convert button when a file is selected
    svgInput.addEventListener('change', function () {
        convertBtn.disabled = svgInput.files.length === 0;
        downloadBtn.disabled = true;
    });

// Convert SVG to PNG when Convert button is clicked
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
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);

                // Convert canvas content to PNG data URL
                const pngDataUrl = canvas.toDataURL('image/png');
                const originalFileName = file.name.split('.').slice(0, -1).join('.') + '.png';
                // Create a download link for the PNG
                downloadBtn.href = pngDataUrl;
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
