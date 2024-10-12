const base64Input = document.getElementById('base64Input');
const decodedImage = document.getElementById('decodedImage');
const imageCard = document.getElementById('imageCard');
const imageInfo = document.getElementById('imageInfo');
const resolution = document.getElementById('resolution');
const mimeType = document.getElementById('mimeType');
const extension = document.getElementById('extension');
const size = document.getElementById('size');
const decodeBtn = document.getElementById('decodeBtn');
const downloadBtn = document.getElementById('downloadBtn');
const toast = document.getElementById('toast');
const mimeToExtension = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/bmp": "bmp",
    "image/tiff": "tif",
    "image/svg+xml": "svg",
};
// Enable decode button if input is present
base64Input.addEventListener('input', function() {
    if (base64Input.value.trim()) {
        decodeBtn.disabled = false; // Enable decode button
        decodeBtn.classList.add("enabled"); // Add enabled class
    } else {
        decodeBtn.disabled = true; // Disable decode button
        decodeBtn.classList.remove("enabled"); // Remove enabled class
    }
});

// Decode Base64 string to image
decodeBtn.addEventListener('click', function() {
    const base64String = base64Input.value.trim();
    if (!base64String) {
        alert("Please enter a valid Base64 string.");
        return;
    }

    // Set the image source
    decodedImage.src = base64String;
    decodedImage.hidden = false; // Show the image
    imageCard.style.display = "block"; // Show the image card

    // Set image info
    decodedImage.onload = function() {
        const mimeTypeValue = base64String.split(';')[0].split(':')[1];
        const fileExtension = mimeToExtension[mimeTypeValue] || 'png';
        resolution.textContent = `Resolution: ${decodedImage.naturalWidth} x ${decodedImage.naturalHeight}`;
        mimeType.textContent = `MIME Type: ${mimeTypeValue}`;
        extension.textContent = `Extension: ${fileExtension}`;
        size.textContent = `Size: ${Math.round(base64String.length * (3 / 4))} bytes`; // Approximate size
        imageInfo.style.display = "block"; // Show image info
        downloadBtn.disabled = false; // Enable download button
        downloadBtn.extension = fileExtension
        downloadBtn.classList.add("enabled"); // Change the button state to enabled
    };
});

// Download image functionality
downloadBtn.addEventListener('click', function() {
    const base64String = base64Input.value.trim();
    const hostName = window.location.hostname.replace(".","-");
    const link = document.createElement('a');
    link.href = base64String;
    link.download = `image-${hostName}.${downloadBtn.extension}`; // Set a default filename
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});