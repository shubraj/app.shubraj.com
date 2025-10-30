# sitemap.py
from django.contrib.sitemaps import Sitemap
from django.urls import URLPattern, reverse
from .urls import urlpatterns, app_name
from datetime import datetime, timedelta
from django.utils import timezone

class StaticViewSitemap(Sitemap):
    """Sitemap for static views that don't change frequently."""
    changefreq = 'monthly'
    priority = 0.5
    protocol = 'https'
    
    def items(self):
        static_patterns = []
        # Add static URL patterns (privacy policy, about page, etc)
        for pattern in urlpatterns:
            if isinstance(pattern, URLPattern) and pattern.name:
                if pattern.name in ['privacy_policy', 'terms', 'home']:
                    static_patterns.append(f"{app_name}:{pattern.name}")
        
        return static_patterns

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # Return a static last modified date for rarely updated pages
        return datetime(2024, 1, 1, tzinfo=timezone.get_current_timezone())

class ToolsSitemap(Sitemap):
    """Sitemap for tool pages that change occasionally."""
    changefreq = 'weekly'
    priority = 0.8
    protocol = 'https'
    
    def items(self):
        tool_patterns = []
        # Include all named app routes except static/utility pages
        exclude = {'privacy_policy', 'terms', 'home', 'sitemap', 'robots.txt'}
        for pattern in urlpatterns:
            if isinstance(pattern, URLPattern) and pattern.name:
                if pattern.name not in exclude:
                    tool_patterns.append(f"{app_name}:{pattern.name}")
        return tool_patterns

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # Return a relatively recent last modified date for tools
        return timezone.now() - timedelta(days=7)


