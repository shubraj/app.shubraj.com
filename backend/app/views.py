from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.cache import cache
from .utils.email_validator import EmailValidator,InvalidEmailSyntax,DomainDoesNotExist,NoMXRecordsFound,EmailNotFound,EmailValidationError

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