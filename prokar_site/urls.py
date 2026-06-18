from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.core.sitemaps import StaticViewSitemap
from apps.blog.sitemaps import PostRuSitemap, PostUzSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'posts_ru': PostRuSitemap,
    'posts_uz': PostUzSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('posts/', include('apps.blog.urls', namespace='blog')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('', include('apps.core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
