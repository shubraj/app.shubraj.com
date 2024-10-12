from django.urls import path
from .views import (
    HomePageView,Base64DecodeImage,Base64EncodeImage,Base64Decoder,
    Base64Encoder,BcryptGenerator,CloudflareEmailDecoder,ColorConverter,CSSBeautifier,
    EmailChecker,ImageColorPicker,IPaddressLookup,JSONBeautifier,MarkdownEditor,
    MD5Generator,RandomPasswordGenerator,SHAGenerator,SVGtoJPG,SVGtoPNG,
    WhatIsMyHeaders,WordCounter,PrivacyPolicy
)

app_name = "app_app"

urlpatterns = [
    path("privacy-policy/",PrivacyPolicy.as_view(),name="privacy_policy"),
    path("word-counter/",WordCounter.as_view(),name="word_counter"),
    path("what-is-my-headers/",WhatIsMyHeaders.as_view(),name="what_is_my_headers"),
    path("svg-to-png/",SVGtoPNG.as_view(),name="svg_to_png"),
    path("svg-to-jpg/",SVGtoJPG.as_view(),name="svg_to_jpg"),
    path("sha-generator/",SHAGenerator.as_view(),name="sha_generator"),
    path("random-password-generator/",RandomPasswordGenerator.as_view(),name="random_password_generator"),
    path("md5-generator/",MD5Generator.as_view(),name="md5_generator"),
    path("markdown-editor/",MarkdownEditor.as_view(),name="markdown_editor"),
    path("json-beautifier/",JSONBeautifier.as_view(),name="json_beautifier"),
    path("ip-address-detail/",IPaddressLookup.as_view(),name="ipaddress_lookup"),
    path("image-color-picker/",ImageColorPicker.as_view(),name="image_color_picker"),
    path("email-checker/",EmailChecker.as_view(),name="email_checker"),
    path("css-beautifier/",CSSBeautifier.as_view(),name="css_beautifier"),
    path("color-converter/",ColorConverter.as_view(),name="color_converter"),
    path("cloudflare-email-decoder/",CloudflareEmailDecoder.as_view(),name="cloudflare_email_decoder"),
    path("bcrypt-generator/",BcryptGenerator.as_view(),name="bcrypt_generator"),
    path("base64-encoder/",Base64Encoder.as_view(),name="base64_encoder"),
    path("base64-decoder/",Base64Decoder.as_view(),name="base64_decoder"),
    path("base64-encode-image/",Base64EncodeImage.as_view(),name="base64_encode_image"),
    path("base64-decode-image/",Base64DecodeImage.as_view(),name="base64_decode_image"),
    path("",HomePageView.as_view(),name="home"),
]