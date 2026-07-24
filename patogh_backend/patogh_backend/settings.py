"""
Django settings for patogh_backend project.
Backend for "بوک پاتوق" (Book Patogh) online bookstore.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- LOAD .env FILE -----------------------------------------------------
# Without this, the values in the .env file are never actually read by
# Django (os.environ only sees real OS environment variables), which meant
# DEBUG defaulted to False and SECRET_KEY stayed at the insecure placeholder,
# causing the RuntimeError below and preventing the server from starting.
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    # python-dotenv not installed; fall back to real environment variables.
    pass


def env_bool(name, default=False):
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=()):
    val = os.environ.get(name)
    if not val:
        return list(default)
    return [item.strip() for item in val.split(',') if item.strip()]


# --- SECURITY ---------------------------------------------------------
# SECRET_KEY and DEBUG now come from the environment so a real deployment
# never accidentally ships with DEBUG=True or the placeholder key.
# DEBUG now defaults to False: if you forget to set DJANGO_DEBUG at all,
# the server fails safe (production-like) instead of leaking stack traces.
# For local development, export (or put in a `.env` you never commit):
#   DJANGO_SECRET_KEY=<a long random string>
#   DJANGO_DEBUG=True
#   DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-only-key-do-not-use-in-production',
)
DEBUG = env_bool('DJANGO_DEBUG', default=False)

if not DEBUG and SECRET_KEY == 'django-insecure-dev-only-key-do-not-use-in-production':
    raise RuntimeError(
        'DJANGO_SECRET_KEY environment variable must be set to a real secret '
        'when DEBUG is False (production).'
    )

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])

# --- ADMIN PANEL URL ---------------------------------------------------
# آدرس پیش‌فرض پنل ادمین جنگو (/admin/) خیلی شناخته‌شده است و اولین چیزی است
# که هر اسکنر/بات خودکار امتحان می‌کند. این مقدار را می‌توان از .env عوض کرد
# (ADMIN_URL_PATH=چیزی-دلخواه)؛ پیش‌فرض یک مسیر تصادفی و سخت‌حدس‌زدنی است.
# نکته: این فقط «پنهان‌کاری» (obscurity) است، نه جایگزین امنیت واقعی — ورود
# به پنل همچنان با یوزرنیم/رمز و throttle محافظت می‌شود؛ فقط پیدا کردنِ خودِ
# صفحه‌ی ورود برای بات‌های خودکار سخت‌تر می‌شود.
ADMIN_URL_PATH = os.environ.get('ADMIN_URL_PATH', 'panel-8f2q7k1z').strip('/') + '/'

# --- PRODUCTION HARDENING (no-ops locally, active once DEBUG=False) ----
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 days
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'

    # اگر پشت یک ریورس‌پروکسی (nginx و ...) که SSL را در همان‌جا terminate
    # می‌کند اجرا می‌شود، بدون این خط، Django فکر می‌کند اتصال همیشه http است
    # (چون خودِ درخواستِ داخلی به gunicorn/uWSGI رمزنگاری‌نشده است) و در
    # نتیجه canonical/og:url و آدرس‌های sitemap.xml را با http:// می‌سازد
    # نه https:// — که برای سئو مشکل‌ساز است (URL نامعتبر/غیرقانونی از نگاه گوگل).
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- APPS ---------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # local apps
    'catalog',
    'blog',
    'inquiries',
    'orders',
    'accounts',
    'advertising',
    'media_library',
    'ai_assistant',
    'seo_pages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'patogh_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'seo_pages.context_processors.store_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'patogh_backend.wsgi.application'

# --- DATABASE ---------------------------------------------------------
# SQLite is enough to start; swap to Postgres for production by changing this block.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- PASSWORDS ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- LOCALIZATION ---------------------------------------------------------
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES ---------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

# --- MEDIA (user-uploaded) FILES -------------------------------------------
# Book cover images are still stored as base64 strings inside the `images`
# JSONField (unchanged), but real uploaded files — PDFs and podcast audio —
# are saved here on disk and served from MEDIA_URL. In production, put a real
# web server (nginx, etc.) in front of this path, or swap to S3/object storage.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- AI ASSISTANT (Grok / Gemini) ------------------------------------------
# Used by the admin-panel "دستیار هوش مصنوعی" chat tab (ai_assistant app).
# Switch providers with AI_PROVIDER=gemini|grok in .env (default: gemini —
# it has a genuinely free API tier, so the admin panel won't hit paid limits
# for normal SEO/blog-writing usage). You only need to set the API key for
# whichever provider you actually pick.
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'gemini')

# Gemini: get a key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')

# Grok (xAI): get a key from https://console.x.ai (API Keys page)
XAI_API_KEY = os.environ.get('XAI_API_KEY', '')
XAI_MODEL = os.environ.get('XAI_MODEL', 'grok-4.3')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- DJANGO REST FRAMEWORK ---------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # NOTE: every viewset/view in this project already sets its own explicit
    # permission_classes (IsAdminOrReadOnly, IsAuthenticated, etc.), so this
    # global default is only a fallback. Kept as AllowAny only for endpoints
    # that intentionally need it (catalog reads, guest checkout, signup/login).
    # Any *new* view you add will be public by default unless you set its own
    # permission_classes — don't forget to do that.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    # Slows down brute-force password guessing / signup spam. Tune the rates
    # to your traffic; 'anon'/'user' apply to every endpoint, 'login' is used
    # explicitly by the login/signup views only.
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'user': '300/minute',
        'login': '10/minute',
        # شروع پرداخت (start-payment) و برگشت از بانک (callback) هر دو به سرور
        # سامان درخواست می‌زنند؛ این نرخ از حلقه‌زدن/سواستفاده روی این دو
        # endpoint جلوگیری می‌کند، بدون این‌که برای یک مشتری واقعی که چند بار
        # تلاش می‌کند مزاحمتی ایجاد کند.
        'payment': '30/minute',
    },
}

# --- CORS ---------------------------------------------------------
# In development, the static HTML storefront may be opened straight from the
# filesystem or a dev server on any port, so we allow all origins here only
# while DEBUG is True. In production, set DJANGO_CORS_ALLOWED_ORIGINS to your
# real frontend domain(s), e.g. "https://patogh-books.example.com".
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = env_list('DJANGO_CORS_ALLOWED_ORIGINS', default=[])
