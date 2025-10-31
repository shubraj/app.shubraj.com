from PIL import Image
from pathlib import Path
import os
import time
import numpy as np
import cv2
from rembg import remove
import piexif
from PIL.ExifTags import TAGS


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


def extract_exif(image_path: str):
    """Extract EXIF metadata as a dict of tag -> value (strings where possible)."""
    try:
        img = Image.open(image_path)
        exif = getattr(img, "_getexif", lambda: None)()
        if not exif:
            return ({"exif": {}}, True)
        # Best-effort stringify with binary handling
        out = {}
        for tag, value in exif.items():
            try:
                name = TAGS.get(tag, str(tag))
            except Exception:
                name = str(tag)
            try:
                if isinstance(value, bytes):
                    if name == 'ComponentsConfiguration' and len(value) == 4:
                        comp_map = {0: 'None', 1: 'Y', 2: 'Cb', 3: 'Cr', 4: 'R', 5: 'G', 6: 'B'}
                        out[name] = ' '.join(comp_map.get(b, str(b)) for b in value)
                    elif name in ('ExifVersion', 'FlashPixVersion') and len(value) == 4:
                        # Versions are ASCII digits like b'0100' → '1.00'
                        try:
                            s = value.decode('ascii', errors='ignore')
                            if s.isdigit() and len(s) == 4:
                                out[name] = f"{s[0]}.{s[1:]}"
                            else:
                                out[name] = s or f"bytes[{len(value)}]"
                        except Exception:
                            out[name] = f"bytes[{len(value)}]: {value.hex()}"
                    else:
                        # If all printable ASCII, show as string; otherwise compact hex
                        if all(32 <= b < 127 for b in value):
                            out[name] = value.decode('ascii', errors='replace')
                        else:
                            out[name] = f"bytes[{len(value)}]: {value.hex()}"
                elif isinstance(value, (list, tuple)):
                    out[name] = ', '.join(str(v) for v in value)
                else:
                    out[name] = str(value)
            except Exception:
                out[name] = repr(value)
        return ({"exif": out}, True)
    except Exception as e:
        return ({"errors": [f"Failed to read EXIF: {e}"]}, False)


def remove_exif(media_dir: Path, image_path: str):
    """Remove EXIF metadata and save a new image (prefer PNG to avoid residual metadata)."""
    try:
        img = Image.open(image_path)
        stem = Path(image_path).stem
        out_name = f"app-shubraj-com-noexif-{time.time_ns()}.png"
        out_path = media_dir / out_name
        if piexif and img.format == 'JPEG':
            try:
                piexif.remove(image_path)
                # After removal, reopen and save as PNG to be consistent
                img2 = Image.open(image_path)
                img2.save(out_path, format='PNG')
                return ({"output_name": out_name}, True)
            except Exception:
                pass
        # Generic approach: drop info/exif and save as PNG
        data = list(img.getdata())
        mode = img.mode
        img_clean = Image.new(mode, img.size)
        img_clean.putdata(data)
        img_clean.save(out_path, format='PNG')
        return ({"output_name": out_name}, True)
    except Exception as e:
        return ({"errors": [f"Failed to remove EXIF: {e}"]}, False)


def add_watermark(media_dir: Path, image_path: str, watermark_text: str = None, watermark_image_path: str = None,
                 position: str = "bottom-right", opacity: float = 0.7, font_size: int = 36,
                 text_color: tuple = (255, 255, 255), output_format: str = "jpg", quality: int = 85):
    """Add text or image watermark to an image.
    
    position: 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'
    opacity: 0.0 to 1.0 (for image watermarks)
    font_size: Size of text watermark
    text_color: RGB tuple for text color
    Returns (result: dict, success: bool)
    """
    errors = []
    
    if not watermark_text and not watermark_image_path:
        return {"errors": ["Either watermark text or watermark image must be provided."]}, False
    
    try:
        base_img = Image.open(image_path)
        # Convert to RGB if needed (for JPG output)
        if output_format.lower() in ('jpg', 'jpeg') and base_img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            bg = Image.new('RGB', base_img.size, (255, 255, 255))
            if base_img.mode == 'P':
                base_img = base_img.convert('RGBA')
            bg.paste(base_img, mask=base_img.split()[-1] if base_img.mode in ('RGBA', 'LA') else None)
            base_img = bg
        elif base_img.mode != 'RGB' and output_format.lower() not in ('png', 'webp'):
            base_img = base_img.convert('RGB')
    except Exception as e:
        return {"errors": [f"Failed to open base image: {e}"]}, False
    
    try:
        from PIL import ImageDraw, ImageFont
        import os
        
        # Calculate position
        img_w, img_h = base_img.size
        positions = {
            'top-left': (10, 10),
            'top-right': (img_w - 100, 10),
            'bottom-left': (10, img_h - 50),
            'bottom-right': (img_w - 100, img_h - 50),
            'center': (img_w // 2 - 50, img_h // 2 - 25),
        }
        pos_x, pos_y = positions.get(position.lower(), positions['bottom-right'])
        
        # Add text watermark
        if watermark_text:
            # Create a transparent layer for the watermark
            watermark_layer = Image.new('RGBA', base_img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            # Try to load a font, fallback to default
            try:
                # Try to use a larger default font
                font_paths = [
                    '/System/Library/Fonts/Supplemental/Arial.ttf',
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                ]
                font = None
                for fp in font_paths:
                    if os.path.exists(fp):
                        try:
                            font = ImageFont.truetype(fp, font_size)
                            break
                        except:
                            continue
                if not font:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Calculate text bounding box
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            # Adjust position based on text size
            if 'right' in position.lower():
                pos_x = img_w - text_w - 10
            elif 'center' in position.lower():
                pos_x = (img_w - text_w) // 2
            else:
                pos_x = 10
            
            if 'bottom' in position.lower():
                pos_y = img_h - text_h - 10
            elif 'center' in position.lower():
                pos_y = (img_h - text_h) // 2
            else:
                pos_y = 10
            
            # Draw text with semi-transparency
            draw.text((pos_x, pos_y), watermark_text, fill=(*text_color, int(255 * opacity)), font=font)
            
            # Composite watermark onto base image
            if base_img.mode == 'RGB':
                base_img = base_img.convert('RGBA')
            base_img = Image.alpha_composite(base_img, watermark_layer)
        
        # Add image watermark
        if watermark_image_path:
            try:
                watermark_img = Image.open(watermark_image_path)
                if watermark_img.mode != 'RGBA':
                    watermark_img = watermark_img.convert('RGBA')
                
                # Resize watermark if too large (max 30% of base image)
                max_w = int(img_w * 0.3)
                max_h = int(img_h * 0.3)
                w_w, w_h = watermark_img.size
                if w_w > max_w or w_h > max_h:
                    scale = min(max_w / w_w, max_h / w_h)
                    new_w = int(w_w * scale)
                    new_h = int(w_h * scale)
                    watermark_img = watermark_img.resize((new_w, new_h), Image.LANCZOS)
                
                # Apply opacity
                alpha = watermark_img.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                watermark_img.putalpha(alpha)
                
                # Calculate position for image watermark
                w_w, w_h = watermark_img.size
                if 'right' in position.lower():
                    pos_x = img_w - w_w - 10
                elif 'center' in position.lower():
                    pos_x = (img_w - w_w) // 2
                else:
                    pos_x = 10
                
                if 'bottom' in position.lower():
                    pos_y = img_h - w_h - 10
                elif 'center' in position.lower():
                    pos_y = (img_h - w_h) // 2
                else:
                    pos_y = 10
                
                # Composite watermark image
                if base_img.mode != 'RGBA':
                    base_img = base_img.convert('RGBA')
                base_img.paste(watermark_img, (pos_x, pos_y), watermark_img)
            except Exception as e:
                errors.append(f"Failed to add image watermark: {e}")
        
        # Save result
        stem = Path(getattr(base_img, 'filename', image_path)).stem
        fmt = (output_format or "jpg").lower()
        if fmt not in ("jpg", "jpeg", "webp", "png"):
            fmt = "jpg"
        ext = 'webp' if fmt == 'webp' else ('png' if fmt == 'png' else 'jpg')
        output_name = f"app-shubraj-com-{stem}-{time.time_ns()}-watermarked.{ext}"
        output_path = media_dir / output_name
        
        # Prepare save
        save_kwargs = {}
        if fmt == 'webp':
            save_kwargs.update({"format": "WEBP", "quality": quality, "method": 6})
        elif fmt in ("jpg", "jpeg"):
            if base_img.mode != 'RGB':
                base_img = base_img.convert('RGB')
            save_kwargs.update({"format": "JPEG", "quality": quality, "optimize": True})
        else:
            compress_level = max(0, min(9, 9 - round((quality - 10) / 90 * 9)))
            save_kwargs.update({"format": "PNG", "optimize": True, "compress_level": compress_level})
        
        try:
            base_img.save(output_path, **save_kwargs)
        except Exception as e:
            return {"errors": [f"Failed to save watermarked image: {e}"]}, False
        
        try:
            out_kb = os.path.getsize(output_path) / 1024.0
        except Exception:
            out_kb = 0.0
        
        if errors:
            return ({"output_name": output_name, "size_kb": out_kb, "warnings": errors}, True)
        return ({"output_name": output_name, "size_kb": out_kb}, True)
        
    except Exception as e:
        return {"errors": [f"Failed to add watermark: {e}"]}, False

