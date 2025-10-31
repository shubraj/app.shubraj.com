from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.cache import cache
from .utils.email_validator import EmailValidator,InvalidEmailSyntax,DomainDoesNotExist,NoMXRecordsFound,EmailNotFound,EmailValidationError
from .utils.dv_tools import process_dv_image
from django.conf import settings
from pathlib import Path
from .utils.image_tools import compress_image_to_target, resize_or_crop_image, remove_background_whiteish, remove_background_ai, extract_exif, remove_exif
from .utils.qr_tools import generate_qr_png, decode_qr_image, generate_barcode_png
from .utils.ssl_checker import get_ssl_certificate_info
from .utils.hash_identifier import identify_hash
from .utils.hsts_checker import check_hsts
from .utils.security_headers_checker import check_security_headers
from .utils.redirect_analyzer import analyze_redirect_chain
import json, time
import jwt

class HomePageView(TemplateView):
    
    template_name = "app/index.html"

class Base64DecodeImage(TemplateView):
    template_name = "app/base64-decode-image.html"

class Base64EncodeImage(TemplateView):
    template_name = "app/base64-encode-image.html"

class Base64Decoder(TemplateView):
    template_name = "app/base64-decoder.html"

class Base64Encoder(TemplateView):
    template_name = "app/base64-encoder.html"

class BcryptGenerator(TemplateView):
    template_name = "app/bcrypt-encryption.html"

class CloudflareEmailDecoder(TemplateView):
    template_name = "app/cloudflare-email-decoder.html"

class ColorConverter(TemplateView):
    template_name = "app/color-converter.html"

class CSSBeautifier(TemplateView):
    template_name = "app/css-beautifier.html"

class EmailChecker(View):
    template_name = "app/email-checker.html"
    CACHE_TIMEOUT = 60 * 60 * 24 * 7

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "")
        cache_key = f'email_check_{email}'

        # Check if the result is already cached
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            # Display cached message based on type
            msg_type = cached_result['type']
            msg_content = cached_result['message']
            getattr(messages, msg_type)(request, msg_content)
            return render(request, self.template_name)

        try:
            _, msg = EmailValidator(email).validate()
            # Cache the success message with its type
            cache.set(cache_key, {'type': 'success', 'message': msg}, timeout=self.CACHE_TIMEOUT)
            messages.success(request, msg)

        except DomainDoesNotExist as e:
            cache.set(cache_key, {'type': 'info', 'message': str(e)}, timeout=self.CACHE_TIMEOUT)
            messages.info(request, str(e))
        except NoMXRecordsFound as e:
            cache.set(cache_key, {'type': 'info', 'message': str(e)}, timeout=self.CACHE_TIMEOUT)
            messages.info(request, str(e))
        except InvalidEmailSyntax as e:
            cache.set(cache_key, {'type': 'error', 'message': str(e)}, timeout=self.CACHE_TIMEOUT)
            messages.error(request, str(e))
        except EmailNotFound as e:
            cache.set(cache_key, {'type': 'error', 'message': str(e)}, timeout=self.CACHE_TIMEOUT)
            messages.error(request, str(e))
        except EmailValidationError as e:
            cache.set(cache_key, {'type': 'error', 'message': f"The email '{email}' does not exist."}, timeout=self.CACHE_TIMEOUT)
            messages.error(request, f"The email '{email}' does not exist.")
        except Exception as e:
            cache.set(cache_key, {'type': 'error', 'message': f"An unexpected error occurred: {str(e)}"}, timeout=self.CACHE_TIMEOUT)
            messages.error(request, f"An unexpected error occurred: {str(e)}")

        return render(request, self.template_name)
class ImageColorPicker(TemplateView):
    template_name = "app/image-color-picker.html"

class IPaddressLookup(TemplateView):
    template_name = "app/ipaddress-lookup.html"

class JSONBeautifier(TemplateView):
    template_name = "app/json-beautifier.html"

class MarkdownEditor(TemplateView):
    template_name = "app/markdown-editor.html"

class MD5Generator(TemplateView):
    template_name = "app/md5-generator.html"

class RandomPasswordGenerator(TemplateView):
    template_name = "app/random-password-generator.html"

class SHAGenerator(TemplateView):
    template_name = "app/sha-generator.html"

class SVGtoPNG(TemplateView):
    template_name = "app/svg-to-png.html"

class SVGtoJPG(TemplateView):
    template_name = "app/svg-to-jpg.html"

class WhatIsMyHeaders(TemplateView):
    template_name = "app/what-is-my-headers.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        headers = self.request.META
        client_headers = {key: headers[key] for key in headers if key.startswith('HTTP_')}
        context['client_headers'] = client_headers
        return context

class WordCounter(TemplateView):
    template_name = "app/word-counter.html"

class PrivacyPolicy(TemplateView):
    template_name = "app/privacy-policy.html"

class TermsAndConditions(TemplateView):
    template_name = "app/terms-and-conditions.html"

class DVPhotoTool(View):
    template_name = "app/dv-photo-tool.html"
    media_dir = Path(settings.MEDIA_ROOT).resolve()
    
    def get(self,request):
        return render(request,self.template_name)
    
    def post(self,request,*args,**kwargs):
        context = {}
        image_file = request.FILES["photo"]
        image_path = f"/tmp/{image_file.name}"
        with open(image_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        result, success = process_dv_image(self.media_dir,image_path)
        context["success"] = success

        def _dedupe_preserve(seq):
            seen = set()
            out = []
            for s in seq:
                if s not in seen:
                    seen.add(s)
                    out.append(s)
            return out

        if not success:
            # result is a list of mixed issue strings; filter out auto-fix notes if any
            raw_issues = [s.strip() for s in result if s]
            issues = [s for s in raw_issues if "Converted" not in s]
            context.update({
                "dv_issues": _dedupe_preserve(issues),
            })
        else:
            # result is (errors_fixed_list, output_filename)
            fixed = [s.strip() for s in (result[0] or [])]
            context.update({
                "dv_actions": _dedupe_preserve(fixed),
                "image": f'{settings.MEDIA_URL}{result[-1]}',
            })
        return render(request,self.template_name,context)

class ImageCompressor(View):
    template_name = "app/image-compressor.html"
    media_dir = Path(settings.MEDIA_ROOT).resolve()

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        context = {}
        image_file = request.FILES.get("image")
        quality = int(request.POST.get("quality", 75))
        out_fmt = request.POST.get("format", "jpg").lower()
        if not image_file:
            return render(request, self.template_name, {"errors": ["Please select an image to compress."]})

        tmp_path = f"/tmp/{image_file.name}"
        with open(tmp_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        result, success = compress_image_to_target(self.media_dir, tmp_path, quality=quality, output_format=out_fmt)
        if not success:
            context["errors"] = result.get("errors", ["Compression failed."])
        else:
            context.update({
                "original_kb": f"{result['original_size_kb']:.2f}",
                "compressed_kb": f"{result['compressed_size_kb']:.2f}",
                "saved_percent": f"{result['saved_percent']:.1f}",
                "image_url": f"{settings.MEDIA_URL}{result['output_name']}",
                "format": out_fmt.upper(),
                "quality": quality,
            })
        return render(request, self.template_name, context)

class ImageResizer(View):
    template_name = "app/image-resizer.html"
    media_dir = Path(settings.MEDIA_ROOT).resolve()

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get("image")
        if not image_file:
            return render(request, self.template_name, {"errors": ["Please select an image."]})

        try:
            width = int(request.POST.get("width", 0))
            height = int(request.POST.get("height", 0))
        except ValueError:
            return render(request, self.template_name, {"errors": ["Width and height must be integers."]})

        mode = request.POST.get("mode", "fit")
        fmt = request.POST.get("format", "jpg")
        quality = int(request.POST.get("quality", 85))

        tmp_path = f"/tmp/{image_file.name}"
        with open(tmp_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        result, success = resize_or_crop_image(self.media_dir, tmp_path, width, height, mode=mode, output_format=fmt, quality=quality)
        if not success:
            return render(request, self.template_name, {"errors": result.get("errors", ["Resize failed."])})

        return render(request, self.template_name, {
            "image_url": f"{settings.MEDIA_URL}{result['output_name']}",
            "width": result["width"],
            "height": result["height"],
            "mode": result["mode"],
            "format": result["format"].upper(),
            "size_kb": f"{result['size_kb']:.2f}",
            "quality": quality,
        })

class URLEncoderDecoder(TemplateView):
    template_name = "app/url-encoder-decoder.html"

class JWTDecoder(TemplateView):
    template_name = "app/jwt-decoder.html"

class UUIDULIDGenerator(TemplateView):
    template_name = "app/uuid-ulid-generator.html"

class UnixTimestampConverter(TemplateView):
    template_name = "app/unix-timestamp-converter.html"

class RegexTester(TemplateView):
    template_name = "app/regex-tester.html"

class TextDiffChecker(TemplateView):
    template_name = "app/text-diff-checker.html"

class QRCodeGenerator(View):
    template_name = "app/qr-code-generator.html"
    media_dir = Path(settings.MEDIA_ROOT).resolve()

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = request.POST.get('data', '')
        ec = request.POST.get('ec', 'M')
        box = int(request.POST.get('box', '10') or 10)
        border = int(request.POST.get('border', '4') or 4)
        result, success = generate_qr_png(self.media_dir, data, error_correction=ec, box_size=box, border=border)
        if not success:
            return render(request, self.template_name, {"errors": result.get("errors", ["Failed to generate QR code."])})
        return render(request, self.template_name, {
            "image_url": f"{settings.MEDIA_URL}{result['output_name']}",
            "data": data,
            "ec": ec,
            "box": box,
            "border": border,
        })

class MarkdownHtmlConverter(TemplateView):
    template_name = "app/markdown-html-converter.html"

class ImageBackgroundRemover(View):
    template_name = "app/image-background-remover.html"
    media_dir = Path(settings.MEDIA_ROOT).resolve()

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        imgf = request.FILES.get('image')
        tol = int(request.POST.get('tolerance', '20') or 20)
        smooth = request.POST.get('smooth', 'on') == 'on'
        if not imgf:
            return render(request, self.template_name, {"errors": ["Please select an image."]})
        tmp_path = f"/tmp/{imgf.name}"
        with open(tmp_path, 'wb') as f:
            for chunk in imgf.chunks():
                f.write(chunk)
        # Try AI remover first; fallback to near-white remover if unavailable or failed
        result, success = remove_background_ai(self.media_dir, tmp_path)
        if not success:
            result, success = remove_background_whiteish(self.media_dir, tmp_path, tolerance=tol, smooth=smooth)
        if not success:
            return render(request, self.template_name, {"errors": result.get('errors', ["Background removal failed."])})
        return render(request, self.template_name, {
            "image_url": f"{settings.MEDIA_URL}{result['output_name']}",
            "tolerance": tol,
            "smooth": smooth,
            "size_kb": f"{result.get('size_kb', 0):.2f}",
        })

class CSVJSONConverter(TemplateView):
    template_name = "app/csv-json-converter.html"

class CaseConverter(TemplateView):
    template_name = "app/case-converter.html"

class PasswordEntropy(TemplateView):
    template_name = "app/password-entropy.html"

class QRCodeScanner(View):
    template_name = "app/qr-code-scanner.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        if not image_file:
            return render(request, self.template_name, {"errors": ["Please select an image with a QR code."]})
        tmp_path = f"/tmp/{image_file.name}"
        with open(tmp_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        result, success = decode_qr_image(tmp_path)
        if not success:
            return render(request, self.template_name, {"errors": result.get('errors', ["Failed to decode QR code."])})
        decoded = result.get('results', [])
        return render(request, self.template_name, {"results": decoded})

class BarcodeGenerator(View):
    template_name = "app/barcode-generator.html"
    media_dir = Path(settings.MEDIA_ROOT).resolve()

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = request.POST.get('data', '').strip()
        kind = request.POST.get('kind', 'code128')
        if not data:
            return render(request, self.template_name, {"errors": ["Please enter data to encode."]})
        if kind == 'qr':
            result, success = generate_qr_png(self.media_dir, data)
        else:
            result, success = generate_barcode_png(self.media_dir, data, kind=kind)
        if not success:
            return render(request, self.template_name, {"errors": result.get('errors', ["Failed to generate barcode."]), "kind": kind, "data": data})
        return render(request, self.template_name, {"image_url": f"{settings.MEDIA_URL}{result['output_name']}", "kind": kind, "data": data})

class SubnetCalculator(TemplateView):
    template_name = "app/subnet-calculator.html"

class ExifTool(View):
    template_name = "app/exif-tool.html"
    media_dir = Path(settings.MEDIA_ROOT).resolve()

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', 'view')
        image_file = request.FILES.get('image')
        if not image_file:
            return render(request, self.template_name, {"errors": ["Please select an image."]})
        tmp_path = f"/tmp/{image_file.name}"
        with open(tmp_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        if action == 'remove':
            result, success = remove_exif(self.media_dir, tmp_path)
            if not success:
                return render(request, self.template_name, {"errors": result.get('errors', ["Failed to remove EXIF"])})
            return render(request, self.template_name, {"removed": True, "image_url": f"{settings.MEDIA_URL}{result['output_name']}"})
        else:
            result, success = extract_exif(tmp_path)
            if not success:
                return render(request, self.template_name, {"errors": result.get('errors', ["Failed to extract EXIF"])})
            return render(request, self.template_name, {"exif_checked": True, "exif": result.get('exif', {})})

class JWTGenerator(View):
    template_name = "app/jwt-generator.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):

        secret = request.POST.get('secret', '')
        claims_text = request.POST.get('claims', '').strip()
        ttl = request.POST.get('ttl', '').strip()
        include_iat = request.POST.get('include_iat', 'on') == 'on'
        kid = request.POST.get('kid', '').strip()

        if not secret:
            return render(request, self.template_name, {"errors": ["Secret is required."], "claims": claims_text, "ttl": ttl, "kid": kid})
        try:
            claims = json.loads(claims_text or '{}')
            if not isinstance(claims, dict):
                raise ValueError('Claims must be a JSON object')
        except Exception as e:
            return render(request, self.template_name, {"errors": [f"Invalid claims JSON: {e}"], "claims": claims_text, "ttl": ttl, "kid": kid})

        now = int(time.time())
        if include_iat:
            claims.setdefault('iat', now)
        if ttl:
            try:
                seconds = int(ttl) * 60
                claims['exp'] = now + max(0, seconds)
            except Exception:
                return render(request, self.template_name, {"errors": ["TTL must be an integer (minutes)."], "claims": claims_text, "ttl": ttl, "kid": kid})

        headers = {"alg": "HS256", "typ": "JWT"}
        if kid:
            headers["kid"] = kid
        try:
            token = jwt.encode(claims, secret, algorithm="HS256", headers=headers)
        except Exception as e:
            return render(request, self.template_name, {"errors": [f"Failed to generate JWT: {e}"], "claims": claims_text, "ttl": ttl, "kid": kid})

        # Decode header/payload for display (without verifying)
        try:
            header = jwt.get_unverified_header(token)
            payload = jwt.decode(token, options={"verify_signature": False})
        except Exception:
            header, payload = {}, {}
        return render(request, self.template_name, {
            "token": token,
            "header": header,
            "payload": payload,
            "claims": claims_text or '{}',
            "ttl": ttl,
            "kid": kid,
        })

class ASCIIArtGenerator(TemplateView):
    template_name = "app/ascii-art-generator.html"

class SSLCertificateChecker(View):
    template_name = "app/ssl-certificate-checker.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        domain = request.POST.get('domain', '').strip()
        
        if not domain:
            return render(request, self.template_name, {
                'errors': ['Please enter a domain name'],
                'domain': domain
            })
        
        # Get SSL certificate information
        cert_info = get_ssl_certificate_info(domain)
        
        if cert_info.get('status') == 'error':
            return render(request, self.template_name, {
                'errors': [cert_info.get('error', 'Unknown error occurred')],
                'domain': domain
            })
        
        return render(request, self.template_name, {
            'domain': domain,
            'certificate_info': cert_info
        })

class HashIdentifier(View):
    template_name = "app/hash-identifier.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        hash_string = request.POST.get('hash', '').strip()
        
        if not hash_string:
            return render(request, self.template_name, {
                'errors': ['Please enter a hash string'],
                'hash_string': hash_string
            })
        
        # Identify the hash
        hash_info = identify_hash(hash_string)
        
        if hash_info.get('error'):
            return render(request, self.template_name, {
                'errors': [hash_info.get('error')],
                'hash_string': hash_string
            })
        
        return render(request, self.template_name, {
            'hash_string': hash_string,
            'hash_info': hash_info
        })

class HSTSChecker(View):
    template_name = "app/hsts-checker.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        domain = request.POST.get('domain', '').strip()
        
        if not domain:
            return render(request, self.template_name, {
                'errors': ['Please enter a domain name'],
                'domain': domain
            })
        
        # Check HSTS configuration
        hsts_info = check_hsts(domain)
        
        if hsts_info.get('status') == 'error' and hsts_info.get('error'):
            return render(request, self.template_name, {
                'errors': [hsts_info.get('error')],
                'domain': domain
            })
        
        return render(request, self.template_name, {
            'domain': domain,
            'hsts_info': hsts_info
        })

class SecurityHeadersChecker(View):
    template_name = "app/security-headers-checker.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        domain = request.POST.get('domain', '').strip()
        
        if not domain:
            return render(request, self.template_name, {
                'errors': ['Please enter a domain name'],
                'domain': domain
            })
        
        # Check security headers
        headers_info = check_security_headers(domain)
        
        if headers_info.get('status') == 'error' and headers_info.get('error'):
            return render(request, self.template_name, {
                'errors': [headers_info.get('error')],
                'domain': domain
            })
        
        return render(request, self.template_name, {
            'domain': domain,
            'headers_info': headers_info
        })

class MorseCodeEncoderDecoder(TemplateView):
    template_name = "app/morse-code-encoder-decoder.html"

class LeetSpeakConverter(TemplateView):
    template_name = "app/leet-speak-converter.html"

class RedirectChainAnalyzer(View):
    template_name = "app/redirect-chain-analyzer.html"
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        url = request.POST.get('url', '').strip()
        
        if not url:
            return render(request, self.template_name, {
                'errors': ['Please enter a URL'],
                'url': url
            })
        
        # Analyze redirect chain
        redirect_info = analyze_redirect_chain(url)
        
        if redirect_info.get('status') == 'error' and redirect_info.get('error'):
            return render(request, self.template_name, {
                'errors': [redirect_info.get('error')],
                'url': url
            })
        
        return render(request, self.template_name, {
            'url': url,
            'redirect_info': redirect_info
        })