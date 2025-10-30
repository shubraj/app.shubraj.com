from PIL import Image
from pathlib import Path
import os
import time
import numpy as np
import cv2
from rembg import remove


def compress_image_to_target(media_dir: Path, image_path: str, quality: int = 75, output_format: str = "jpg"):
    """Compress an image server-side.

    Returns (result: dict, success: bool)
    result keys on success: original_size_kb, compressed_size_kb, saved_percent, output_name
    On failure: {"errors": [..]}
    """
    errors = []
    try:
        img = Image.open(image_path)
    except Exception as e:
        return {"errors": [f"Failed to open image: {e}"]}, False

    # Derive output name
    stem = Path(getattr(img, 'filename', image_path)).stem
    fmt = (output_format or "jpg").lower()
    if fmt not in ("jpg", "jpeg", "webp", "png"):
        fmt = "jpg"
    ext = 'webp' if fmt == 'webp' else ('png' if fmt == 'png' else 'jpg')
    output_name = f"app-shubraj-com-{stem}-{time.time_ns()}-compressed.{ext}"
    output_path = media_dir / output_name

    # Determine mode
    # Prepare image according to output format
    if fmt in ("jpg", "jpeg"):
        img_for_save = img.convert('RGB') if img.mode != 'RGB' else img
    elif fmt == 'webp':
        # WebP supports alpha; keep mode
        img_for_save = img
    else:  # png
        img_for_save = img  # keep as-is to preserve alpha

    # Original size (KB)
    try:
        original_size_kb = os.path.getsize(image_path) / 1024.0
    except Exception:
        original_size_kb = 0.0

    # Save compressed
    save_kwargs = {}
    if fmt == 'webp':
        save_kwargs.update({"format": "WEBP", "quality": quality, "method": 6})
    elif fmt in ("jpg", "jpeg"):
        save_kwargs.update({"format": "JPEG", "quality": quality, "optimize": True})
    else:  # png
        # PNG uses lossless compression; Pillow uses quality-like via optimize and compress_level (0-9)
        # Map quality 10-100 to compress_level 9-0 (higher quality -> lower compression level)
        compress_level = max(0, min(9, 9 - round((quality - 10) / 90 * 9)))
        save_kwargs.update({"format": "PNG", "optimize": True, "compress_level": compress_level})

    try:
        img_for_save.save(output_path, **save_kwargs)
    except Exception as e:
        return {"errors": [f"Failed to save compressed image: {e}"]}, False

    compressed_size_kb = os.path.getsize(output_path) / 1024.0
    saved_percent = max(0.0, (1 - (compressed_size_kb / original_size_kb)) * 100) if original_size_kb else 0.0

    return ({
        "original_size_kb": original_size_kb,
        "compressed_size_kb": compressed_size_kb,
        "saved_percent": saved_percent,
        "output_name": output_name,
    }, True)


def resize_or_crop_image(media_dir: Path, image_path: str, width: int, height: int, mode: str = "fit", output_format: str = "jpg", quality: int = 85):
    """Resize or crop image.

    mode: 'fit' (contain, preserve aspect) or 'fill' (cover, center-crop)
    output_format: jpg | png | webp
    Returns (result: dict, success: bool) like compressor.
    """
    errors = []
    try:
        img = Image.open(image_path)
    except Exception as e:
        return {"errors": [f"Failed to open image: {e}"]}, False

    if width <= 0 or height <= 0:
        return {"errors": ["Width and height must be positive integers."]}, False

    fmt = (output_format or "jpg").lower()
    if fmt not in ("jpg", "jpeg", "webp", "png"):
        fmt = "jpg"

    # Compute resize
    src_w, src_h = img.size
    if mode == "fill":
        # cover: scale to fill then center crop
        scale = max(width / src_w, height / src_h)
        new_w, new_h = int(round(src_w * scale)), int(round(src_h * scale))
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        left = max(0, (new_w - width) // 2)
        top = max(0, (new_h - height) // 2)
        img_out = img_resized.crop((left, top, left + width, top + height))
    else:
        # fit: contain within box, preserve aspect; pad not applied, just smaller side
        scale = min(width / src_w, height / src_h)
        new_w, new_h = int(round(src_w * scale)), int(round(src_h * scale))
        img_out = img.resize((new_w, new_h), Image.LANCZOS)

    # Build output
    stem = Path(getattr(img, 'filename', image_path)).stem
    ext = 'webp' if fmt == 'webp' else ('png' if fmt == 'png' else 'jpg')
    output_name = f"app-shubraj-com-{stem}-{time.time_ns()}-{width}x{height}-{mode}.{ext}"
    output_path = media_dir / output_name

    # Prepare save
    save_kwargs = {}
    if fmt == 'webp':
        save_kwargs.update({"format": "WEBP", "quality": quality, "method": 6})
    elif fmt in ("jpg", "jpeg"):
        img_out = img_out.convert('RGB') if img_out.mode != 'RGB' else img_out
        save_kwargs.update({"format": "JPEG", "quality": quality, "optimize": True})
    else:
        compress_level = max(0, min(9, 9 - round((quality - 10) / 90 * 9)))
        save_kwargs.update({"format": "PNG", "optimize": True, "compress_level": compress_level})

    try:
        img_out.save(output_path, **save_kwargs)
    except Exception as e:
        return {"errors": [f"Failed to save resized image: {e}"]}, False

    try:
        out_kb = os.path.getsize(output_path) / 1024.0
    except Exception:
        out_kb = 0.0

    return ({
        "output_name": output_name,
        "width": width,
        "height": height,
        "mode": mode,
        "format": fmt,
        "size_kb": out_kb,
    }, True)


def remove_background_whiteish(media_dir: Path, image_path: str, tolerance: int = 20, smooth: bool = True):
    """Remove near-white background by making those pixels transparent.

    tolerance: 0-255; higher removes more background.
    Returns (result: dict, success: bool)
    """
    try:
        img = Image.open(image_path).convert('RGBA')
    except Exception as e:
        return {"errors": [f"Failed to open image: {e}"]}, False

    arr = np.array(img)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]

    # Threshold for near-white
    thr = max(0, min(255, 255 - int(tolerance or 0)))
    mask_bg = (rgb[:, :, 0] >= thr) & (rgb[:, :, 1] >= thr) & (rgb[:, :, 2] >= thr)

    if smooth:
        kernel = np.ones((3, 3), np.uint8)
        mask_bg = cv2.morphologyEx(mask_bg.astype(np.uint8) * 255, cv2.MORPH_OPEN, kernel)
        mask_bg = cv2.GaussianBlur(mask_bg, (3, 3), 0) > 127

    # Set transparent for background
    alpha[mask_bg] = 0
    arr[:, :, 3] = alpha

    out_img = Image.fromarray(arr)
    name = f"app-shubraj-com-bgrm-{time.time_ns()}.png"
    out_path = media_dir / name
    try:
        out_img.save(out_path, format='PNG')
    except Exception as e:
        return {"errors": [f"Failed to save result: {e}"]}, False

    try:
        out_kb = os.path.getsize(out_path) / 1024.0
    except Exception:
        out_kb = 0.0

    return ({"output_name": name, "size_kb": out_kb}, True)


def remove_background_ai(media_dir: Path, image_path: str):
    """High-quality background removal using rembg (U2Net). Returns PNG with alpha."""

    try:
        with open(image_path, 'rb') as f:
            inp = f.read()
        out_bytes = remove(inp)
    except Exception as e:
        return {"errors": [f"AI removal failed: {e}"]}, False

    name = f"app-shubraj-com-bgrm-ai-{time.time_ns()}.png"
    out_path = media_dir / name
    try:
        with open(out_path, 'wb') as f:
            f.write(out_bytes)
    except Exception as e:
        return {"errors": [f"Failed to save result: {e}"]}, False

    try:
        out_kb = os.path.getsize(out_path) / 1024.0
    except Exception:
        out_kb = 0.0

    return ({"output_name": name, "size_kb": out_kb}, True)

