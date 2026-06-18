from django.utils import translation

_NO_INDEX_PREFIXES = ('/admin/', '/ckeditor/', '/i18n/', '/__reload__/')


class AdminLocaleMiddleware:
    """Force Russian language for all admin pages."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            translation.activate('ru')
            request.LANGUAGE_CODE = 'ru'
        return self.get_response(request)


class AdminRobotsMiddleware:
    """Prevent admin and internal URLs from being indexed by search engines."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if any(request.path.startswith(p) for p in _NO_INDEX_PREFIXES):
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
