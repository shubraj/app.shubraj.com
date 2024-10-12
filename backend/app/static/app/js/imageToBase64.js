const imageInput = document.getElementById('imageInput');
const base64Output = document.getElementById('base64Output');
const encodeBtn = document.getElementById('encodeBtn');
const copyBtn = document.getElementById('copyBtn');
const toast = document.getElementById('toast');

// Disable the encode button initially
encodeBtn.disabled = true;

// Enable the encode button when a file is selected
imageInput.addEventListener('change', function() {
    const file = imageInput.files[0];
    if (file) {
        encodeBtn.disabled = false; // Enable the button if an image is selected
    } else {
        encodeBtn.disabled = true; // Disable if not an image
    }
});

// Encode the image to Base64
encodeBtn.addEventListener('click', function() {
    const file = imageInput.files[0];
    if (!file) {
        alert("Please select an image.");
        return;
    }

    const reader = new FileReader();
    reader.onloadend = function() {
        base64Output.value = reader.result;
        copyBtn.disabled = false;
    };
    reader.readAsDataURL(file);
});

// Copy Base64 output to clipboard with toast notification
copyBtn.addEventListener('click', function() {
    navigator.clipboard.writeText(base64Output.value).then(() => {
        // Show toast notification
        toast.className = "toast show";
        setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
    });
});
