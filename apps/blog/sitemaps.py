from django.contrib.sitemaps import Sitemap
from .models import Post


class PostRuSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_active=True).order_by('-created_at')

    def location(self, obj):
        return f'/posts/{obj.slug_ru}/'

    def lastmod(self, obj):
        return obj.updated_at


class PostUzSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_active=True).order_by('-created_at')

    def location(self, obj):
        return f'/posts/{obj.slug_uz}/'

    def lastmod(self, obj):
        return obj.updated_at
