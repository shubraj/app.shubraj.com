from django.shortcuts import render
from django.views.generic import TemplateView

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

class EmailChecker(TemplateView):
    template_name = "app/email-checker.html"

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