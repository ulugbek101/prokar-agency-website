from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    protocol = 'https'

    pages = [
        ('core:home',      1.0, 'weekly'),
        ('blog:post_list', 0.9, 'daily'),
        ('core:about',     0.7, 'monthly'),
    ]

    def items(self):
        return self.pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]
