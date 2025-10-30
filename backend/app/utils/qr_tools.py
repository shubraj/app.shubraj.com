from pathlib import Path
import time
import qrcode
import cv2
import numpy as np


def generate_qr_png(media_dir: Path, data: str, version: int | None = None, error_correction: str = 'M', box_size: int = 10, border: int = 4):
    """Generate a QR code PNG saved to media directory.

    error_correction: one of 'L','M','Q','H'
    Returns (result: dict, success: bool)
    """
    if not data:
        return {"errors": ["No data provided."]}, False

    ec_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }
    ec = ec_map.get((error_correction or 'M').upper(), qrcode.constants.ERROR_CORRECT_M)

    qr = qrcode.QRCode(
        version=version or None,
        error_correction=ec,
        box_size=max(1, int(box_size or 10)),
        border=max(1, int(border or 4)),
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    name = f"app-shubraj-com-qr-{time.time_ns()}.png"
    out_path = media_dir / name
    img.save(out_path)
    return ({"output_name": name}, True)

def decode_qr_image(image_path: str):
    """Decode QR codes from an image. Returns list of decoded strings.

    Uses OpenCV QRCodeDetector; supports multiple codes when available.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"errors": ["Failed to read image"]}, False
    except Exception as e:
        return {"errors": [f"Failed to read image: {e}"]}, False

    detector = cv2.QRCodeDetector()
    try:
        # Try multi first
        data_list, points, _ = detector.detectAndDecodeMulti(img)
        if data_list is not None and any(data_list):
            decoded = [s for s in data_list if s]
            return ({"results": decoded}, True)
        # Fallback single
        data, points, _ = detector.detectAndDecode(img)
        if data:
            return ({"results": [data]}, True)
        return ({"results": []}, True)
    except Exception as e:
        return {"errors": [f"Decode error: {e}"]}, False


