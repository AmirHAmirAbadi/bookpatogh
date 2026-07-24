from pathlib import Path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path

from . import admin_branding  # noqa: F401  # سربرگ/لیبل‌های فارسیِ پنل ادمین را تنظیم می‌کند

FRONTEND_INDEX = Path(__file__).resolve().parent.parent / 'frontend' / 'index.html'


def serve_frontend_app(request, *args, **kwargs):
    """
    اپ تعاملی (سبد خرید، پرداخت، ورود/عضویت، پنل ادمین...) همان فایل تک‌صفحه‌ای
    قدیمی است؛ اینجا فقط همان‌طور که هست از دیسک خوانده و برگردانده می‌شود.
    آدرس‌های داخلی‌اش (#/shop ، #/book/ID و ...) همچنان توسط جاوااسکریپت خودش
    کنترل می‌شوند و کاری به مسیرهای واقعی صفحات سئو در پایین ندارند.
    """
    html = FRONTEND_INDEX.read_text(encoding='utf-8')
    return HttpResponse(html, content_type='text/html; charset=utf-8')


urlpatterns = [
    path(settings.ADMIN_URL_PATH, admin.site.urls),
    path('api/', include('catalog.urls')),
    path('api/', include('blog.urls')),
    path('api/', include('inquiries.urls')),
    path('api/', include('orders.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('advertising.urls')),
    path('api/', include('media_library.urls')),
    path('api/', include('ai_assistant.urls')),

    # اپ تعاملی/فروشگاهی قدیمی (SPA) — همه‌چیز زیر /app/ به همین ویو می‌رود
    # چون خودِ آن با هش (#/...) مسیریابی می‌کند، نه با مسیر واقعی.
    re_path(r'^app/.*$', serve_frontend_app, name='frontend_app'),

    # صفحات جداگانه و قابل ایندکس برای سئو (هر کتاب/نویسنده/پست آدرس خودش را دارد)
    path('', include('seo_pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
