from PIL import Image
import cv2
import numpy as np
import os

def process_dv_image(image_path, output_path="output_dv_image.jpg", is_scanned=False):
    # Load the image
    img = Image.open(image_path)

    # Check format
    if img.format != "JPEG":
        return "Image is not in JPEG format. Please provide a JPEG image.", False

    # Check size and resize to 600x600 pixels if needed
    if img.size != (600, 600):
        img = img.resize((600, 600), Image.LANCZOS)
        print("Resized image to 600x600 pixels.")

    # Additional checks for scanned photos
    if is_scanned:
        if img.size != (600, 600):
            return "For scanned images, please provide an image with 2x2 inches (51x51 mm) dimensions.", False
        elif img.info.get("dpi", (0, 0))[0] != 300:
            return "Scanned image does not have a resolution of 300 DPI.", False
        else:
            print("Scanned image meets the 2x2 inches and 300 DPI requirements.")

    # Convert to OpenCV format for further checks
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Face detection with OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(img_cv, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    # Ensure there is exactly one face detected
    if len(faces) == 0:
        return "No face detected in the image. Please ensure the face is visible.", False
    elif len(faces) > 1:
        return "Multiple faces detected. Please ensure only one face is visible in the image.", False
    else:
        print("Single face detected in the image.")

    # Center crop to show upper body only
    x, y, w, h = faces[0]
    face_center_y = y + h // 2

    # Define crop region (from above the head to below the shoulders, estimated for a head-centered crop)
    top = max(0, y - int(h * 0.5))
    bottom = min(img_cv.shape[0], face_center_y + int(h * 1.2))

    # Crop image for upper body composition
    img_cv_cropped = img_cv[top:bottom, :]
    img_cropped = Image.fromarray(cv2.cvtColor(img_cv_cropped, cv2.COLOR_BGR2RGB)).resize((600, 600), Image.LANCZOS)

    # Check lighting on cropped image
    gray = cv2.cvtColor(np.array(img_cropped), cv2.COLOR_RGB2GRAY)
    brightness = np.mean(gray)
    brightness_threshold = 100  # Adjust if needed
    if brightness < brightness_threshold:
        return "Image is too dark. Ensure the face is well-lit.", False
    else:
        print("Image lighting is adequate.")

    # Enhanced Background Detection
    img_np = np.array(img_cropped)
    white_threshold = 230  # Lowered to be more inclusive of near-white tones

    # Define smaller region around the face as non-background
    margin = 20  # Slight margin around face bounding box
    background_mask = np.ones(img_np.shape[:2], dtype=np.uint8)
    background_mask[y-margin: y+h+margin, x-margin: x+w+margin] = 0  # Mask the face area

    # Calculate white pixel coverage outside the face area
    white_pixels = (img_np[:, :, :3] > white_threshold).all(axis=2) & (background_mask == 1)
    white_coverage = np.sum(white_pixels) / np.sum(background_mask == 1) if np.sum(background_mask == 1) > 0 else 0  # Avoid division by zero

    # Debug: print white coverage percentage
    print(f"White coverage percentage in background: {white_coverage * 100:.2f}%")

    required_white_coverage = 0.85  # Require 85% white pixels in background
    if white_coverage < required_white_coverage:
        return "Background is not sufficiently white. Ensure a plain white or off-white background.", False

    # Save image if all conditions are met and check file size
    img_cropped.save(output_path, "JPEG", quality=85)
    file_size_kb = os.path.getsize(output_path) / 1024  # File size in KB

    if file_size_kb > 240:
        os.remove(output_path)  # Delete the file if size exceeds the limit
        return f"Image file size is {file_size_kb:.2f} KB, which exceeds the 240 KB limit.", False
    else:
        print(f"Image file size is {file_size_kb:.2f} KB, which is within the limit.")

    return "Image meets all DV requirements with correct cropping and white or off-white background.", True

# Example usage
image_path = "test.jpg"
output_path = "output_dv_image.jpg"
is_scanned = False  # Set this to True if using a scanned photo
message, status = process_dv_image(image_path, output_path, is_scanned)
print(message)
if status:
    print("Image is compliant with DV Program requirements.")
else:
    print("Image did not meet all requirements.")
