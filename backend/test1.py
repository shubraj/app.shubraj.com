from PIL import Image
import cv2
import numpy as np
import os
import time
from pathlib import Path

def process_dv_image(image_path):
    errors = []  # List to accumulate all errors

    # Load the image
    img = Image.open(image_path)
    filename = Path(img.filename).stem
    extension = Path(img.filename).suffix
    output_path = f"app-shubraj-com-{filename}-{time.time_ns()}{extension}"

    # Check format
    if img.format != "JPEG":
        errors.append("Image is not in JPEG format. Please provide a JPEG image.")

    # Check size and resize to 600x600 pixels if needed
    if img.size != (600, 600):
        img = img.resize((600, 600), Image.LANCZOS)

    # Additional checks for scanned photos
    if img.size != (600, 600):
        errors.append("For scanned images, please provide an image with 2x2 inches (51x51 mm) dimensions.")
    elif img.info.get("dpi", (300, 300))[0] != 300:
        errors.append("Scanned image does not have a resolution of 300 DPI.")

    # Convert to OpenCV format for further checks
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Face detection with OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(img_cv, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    # Ensure there is exactly one face detected
    if len(faces) == 0:
        errors.append("No face detected in the image. Please ensure the face is visible.")
    elif len(faces) > 1:
        errors.append("Multiple faces detected. Please ensure only one face is visible in the image.")

    # Check for glasses and masks
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    face = faces[0]
    x, y, w, h = face
    roi_gray = cv2.cvtColor(img_cv[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
    eyes = eye_cascade.detectMultiScale(roi_gray)

    if len(eyes) < 2:  # If less than two eyes detected, may indicate glasses or mask
        errors.append("The detected face may be wearing glasses or a mask. Please ensure the face is unobstructed.")

    # Center crop to show upper body only
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
    brightness_threshold = 80  # Adjust if needed
    if brightness < brightness_threshold:
        errors.append("Image is too dark. Ensure the face is well-lit.")

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

    required_white_coverage = 0.45  # Require 45% white pixels in background
    if white_coverage < required_white_coverage:
        errors.append("Background is not sufficiently white. Ensure a plain white or off-white background.")

    
    # Save image if all conditions are met and check file size
    img_cropped.save(output_path, "JPEG", quality=85)
    file_size_kb = os.path.getsize(output_path) / 1024  # File size in KB

    if file_size_kb > 240:
        os.remove(output_path)  # Delete the file if size exceeds the limit
        errors.append(f"Image file size is {file_size_kb:.2f} KB, which exceeds the 240 KB limit.")

    return output_path, True


# Example usage
image_path = "random.jpg"
output_path = "output_dv_image.jpg"
message, status = process_dv_image(image_path)
if status:
    print("Image is compliant with DV Program requirements.")
else:
    print(message)
