# sitemap.py
from django.contrib.sitemaps import Sitemap
from django.urls import URLPattern,reverse
from .urls import urlpatterns,app_name

class DynamicViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1.0
    protocol = "https"
    
    def items(self):
        static_patterns = []

        for pattern in urlpatterns:
            if isinstance(pattern, URLPattern) and pattern.name:
                if not pattern.pattern.converters:
                    static_patterns.append(f"{app_name}:{pattern.name}")
        
        return static_patterns

    def location(self, item):
        return reverse(item)


