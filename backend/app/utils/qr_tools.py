from pathlib import Path
import time
import qrcode
import cv2
import numpy as np
from barcode import Code128, EAN13
from barcode.writer import ImageWriter


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
        # Try multi first (OpenCV versions differ in return signature)
        multi_res = detector.detectAndDecodeMulti(img)
        if isinstance(multi_res, tuple):
            if len(multi_res) == 4:
                retval, data_list, points, _ = multi_res
                if retval and data_list:
                    decoded = [s for s in data_list if s]
                    if decoded:
                        return ({"results": decoded}, True)
            elif len(multi_res) == 3:
                data_list, points, _ = multi_res
                if data_list:
                    decoded = [s for s in data_list if s]
                    if decoded:
                        return ({"results": decoded}, True)

        # Fallback single
        single_res = detector.detectAndDecode(img)
        if isinstance(single_res, tuple) and len(single_res) >= 2:
            data = single_res[0]
        else:
            data = single_res
        if data:
            return ({"results": [data]}, True)
        return ({"results": []}, True)
    except Exception as e:
        return {"errors": [f"Decode error: {e}"]}, False

def generate_barcode_png(media_dir: Path, data: str, kind: str = 'code128'):
    """Generate barcode PNG for Code128 or EAN13. Returns filename.

    kind: 'code128' | 'ean13'
    EAN13 requires 12 digits (the 13th checksum is computed).
    """
    if not data:
        return {"errors": ["No data provided."]}, False
    kind = (kind or 'code128').lower()
    try:
        if kind == 'ean13':
            stripped = ''.join(ch for ch in data if ch.isdigit())
            if len(stripped) != 12:
                return {"errors": ["EAN-13 requires exactly 12 digits (checksum auto-added)."]}, False
            cls = EAN13
            payload = stripped
        else:
            cls = Code128
            payload = data

        name = f"app-shubraj-com-barcode-{kind}-{time.time_ns()}"
        out_path = media_dir / f"{name}.png"
        bc = cls(payload, writer=ImageWriter())
        bc.write(open(out_path, 'wb'))
        return ({"output_name": f"{name}.png"}, True)
    except Exception as e:
        return {"errors": [f"Barcode error: {e}"]}, False


