from PIL import Image
from pathlib import Path
import os
import time
from typing import Dict, List
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


def pdf_to_images(media_dir: Path, pdf_path: str, max_pages: int = 10, dpi: int = 200, output_format: str = "png") -> tuple:
    """
    Convert PDF pages to images.
    
    Args:
        media_dir: Directory to save output images
        pdf_path: Path to PDF file
        max_pages: Maximum number of pages to convert (default: 10)
        dpi: Resolution for image conversion (default: 200)
        output_format: Output image format - 'png' or 'jpg' (default: 'png')
        
    Returns:
        Tuple of (result_dict, success_bool)
    """
    if not PDF2IMAGE_AVAILABLE:
        return {
            'errors': ['PDF to image conversion requires pdf2image library. Please install it with: pip install pdf2image']
        }, False
    
    errors = []
    
    # Validate output format
    fmt = output_format.lower()
    if fmt not in ('png', 'jpg', 'jpeg'):
        fmt = 'png'
    
    try:
        # Convert PDF to images
        # Note: This requires poppler-utils to be installed on the system
        images = convert_from_path(pdf_path, dpi=dpi)
        
        total_pages = len(images)
        
        if total_pages == 0:
            return {'errors': ['PDF file contains no pages']}, False
        
        # Check page limit
        if total_pages > max_pages:
            errors.append(f'PDF has {total_pages} pages, but maximum allowed is {max_pages}. Only first {max_pages} pages will be converted.')
            pages_to_convert = max_pages
        else:
            pages_to_convert = total_pages
        
        # Get PDF filename stem for naming
        pdf_stem = Path(pdf_path).stem
        
        # Convert pages to images
        output_files = []
        total_size = 0
        
        for page_num in range(pages_to_convert):
            img = images[page_num]
            
            # Prepare for saving
            if fmt in ('jpg', 'jpeg'):
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for JPEG
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    bg.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = bg
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
            
            # Generate output filename
            output_name = f"app-shubraj-com-{pdf_stem}-page-{page_num + 1}-{time.time_ns()}.{fmt}"
            output_path = media_dir / output_name
            
            # Save image
            save_kwargs = {}
            if fmt in ('jpg', 'jpeg'):
                save_kwargs = {'format': 'JPEG', 'quality': 95, 'optimize': True}
            else:
                save_kwargs = {'format': 'PNG', 'optimize': True}
            
            try:
                img.save(output_path, **save_kwargs)
                file_size = os.path.getsize(output_path) / 1024.0  # Size in KB
                total_size += file_size
                
                output_files.append({
                    'filename': output_name,
                    'page': page_num + 1,
                    'size_kb': round(file_size, 2)
                })
            except Exception as e:
                errors.append(f'Failed to save page {page_num + 1}: {str(e)}')
        
        if not output_files:
            return {'errors': errors if errors else ['Failed to convert any pages']}, False
        
        result = {
            'total_pages': total_pages,
            'converted_pages': len(output_files),
            'output_files': output_files,
            'total_size_kb': round(total_size, 2),
            'format': fmt.upper(),
            'dpi': dpi
        }
        
        if errors:
            result['warnings'] = errors
        
        return result, True
        
    except Exception as e:
        error_msg = str(e).lower()
        if 'poppler' in error_msg or 'pdf2image' in error_msg:
            return {
                'errors': ['PDF conversion requires poppler-utils. Please ensure it is installed on the server.']
            }, False
        elif 'not a pdf' in error_msg or 'invalid' in error_msg:
            return {
                'errors': ['Invalid PDF file or file is corrupted']
            }, False
        else:
            return {
                'errors': [f'Failed to convert PDF: {str(e)}']
            }, False

