from pathlib import Path
from decouple import config, Csv
from environs import Env as _Env

_env = _Env()
_env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    # django-unfold must come before django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    # modeltranslation must come before django.contrib.admin
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'tailwind',
    'theme',
    'django_browser_reload',
    'ckeditor',
    'ckeditor_uploader',
    # local apps
    'apps.blog',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'prokar_site.middleware.AdminLocaleMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

ROOT_URLCONF = 'prokar_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'apps.core.context_processors.feedback_form',
            ],
        },
    },
]

WSGI_APPLICATION = 'prokar_site.wsgi.application'

# ── Database ──────────────────────────────────────────────────────────────────
USE_SQLITE = config('USE_SQLITE', default=True, cast=bool)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'ru'
LANGUAGES = [
    ('ru', 'Русский'),
    ('uz', "O'zbek"),
]
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

# ── Static & media ────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Silence the CKEditor 4 EOL warning — acknowledged, upgrade planned
SILENCED_SYSTEM_CHECKS = ['ckeditor.W001']

# ── Tailwind ──────────────────────────────────────────────────────────────────
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ['127.0.0.1']

# ── CKEditor ──────────────────────────────────────────────────────────────────
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar_Full': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike',
             'Subscript', 'Superscript', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
             'Blockquote', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['TextColor', 'BGColor'],
            ['Source', 'ShowBlocks', '-', 'Maximize'],
            '/',
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-',
             'Undo', 'Redo'],
            ['Find', 'Replace', '-', 'SelectAll'],
            ['Scayt'],
        ],
        'toolbar': 'Full',
        'height': 480,
        'width': '100%',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',
            'image2',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath',
            'codesnippet',
        ]),
    },
}

# ── Django Unfold ─────────────────────────────────────────────────────────────
# ── Telegram notifications ────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = _env.str('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_ADMIN_IDS = _env.list('TELEGRAM_ADMIN_IDS', default=[])

# ── Django Unfold ─────────────────────────────────────────────────────────────
UNFOLD = {
    "SITE_TITLE": "Prokar Ekspert Audit",
    "SITE_HEADER": "Prokar Admin",
    "SITE_SUBHEADER": "Управление контентом",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "240 249 255",
            "100": "224 242 254",
            "200": "186 230 253",
            "300": "125 211 252",
            "400": "56 189 248",
            "500": "14 165 233",
            "600": "2 132 199",
            "700": "3 105 161",
            "800": "7 89 133",
            "900": "12 74 110",
            "950": "8 47 73",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Блог",
                "separator": True,
                "items": [
                    {
                        "title": "Публикации",
                        "icon": "article",
                        "link": "/admin/blog/post/",
                    },
                    {
                        "title": "Теги",
                        "icon": "label",
                        "link": "/admin/blog/tag/",
                    },
                ],
            },
            {
                "title": "Команда",
                "separator": True,
                "items": [
                    {
                        "title": "Специалисты",
                        "icon": "badge",
                        "link": "/admin/core/staff/",
                    },
                ],
            },
            {
                "title": "Документы",
                "separator": True,
                "items": [
                    {
                        "title": "Документы и сертификаты",
                        "icon": "description",
                        "link": "/admin/core/certificate/",
                    },
                ],
            },
            {
                "title": "Обращения",
                "separator": True,
                "items": [
                    {
                        "title": "Обращения клиентов",
                        "icon": "mail",
                        "link": "/admin/core/feedback/",
                    },
                ],
            },
            {
                "title": "Пользователи",
                "separator": True,
                "items": [
                    {
                        "title": "Пользователи",
                        "icon": "person",
                        "link": "/admin/auth/user/",
                    },
                    {
                        "title": "Группы",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
                ],
            },
        ],
    },
}
