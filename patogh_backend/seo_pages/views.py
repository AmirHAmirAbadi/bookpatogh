"""
صفحات «واقعی» و مجزا (هر کدام آدرس خودشان را دارند) که برای موتورهای جست‌وجو
رندر می‌شوند: صفحه‌ی هر کتاب، هر نویسنده، هر پست وبلاگ و لیست‌های آن‌ها.

این صفحات کاملاً سمت سرور رندر می‌شوند (بدون نیاز به اجرای جاوااسکریپت) تا
گوگل بتواند محتوای واقعی هرکدام را همان لحظه‌ی اول ببیند و ایندکس کند؛ تجربه‌ی
خرید تعاملی (سبد خرید، پرداخت، ورود/عضویت و ...) همچنان در برنامه‌ی تک‌صفحه‌ای
اصلی (SPA) در آدرس /app/ انجام می‌شود. هر صفحه‌ی سئو یک دکمه‌ی «مشاهده در
فروشگاه» دارد که با هش مناسب مستقیم به همان کتاب/نویسنده در SPA می‌رود.
"""
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify
from urllib.parse import quote

from catalog.models import Author, Book
from blog.models import Post
from media_library.models import PdfItem, Podcast

SITE_NAME = 'پاتوق بوک'
SITE_DESCRIPTION_SUFFIX = 'در پاتوق بوک؛ فروشگاه اینترنتی خرید کتاب با ارسال سریع به سراسر ایران.'


def _truncate(text, length=155):
    text = strip_tags(text or '').strip()
    text = ' '.join(text.split())
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '…'


def _book_meta_description(book):
    if book.description and book.description.strip():
        return _truncate(book.description)
    return _truncate(
        f'خرید کتاب «{book.title}» نوشته‌ی {book.author.name} با قیمت '
        f'{book.final_price:,} تومان و ارسال سریع {SITE_DESCRIPTION_SUFFIX}'
    )


def _author_meta_description(author):
    if author.bio and author.bio.strip():
        return _truncate(author.bio)
    return _truncate(f'کتاب‌های {author.name} برای خرید آنلاین {SITE_DESCRIPTION_SUFFIX}')


def home(request):
    featured = Book.objects.select_related('author').filter(featured=True)[:8]
    latest = Book.objects.select_related('author').order_by('-created_at')[:12]
    authors = Author.objects.all()[:8]
    posts = Post.objects.filter(published=True).order_by('-created_at')[:3]
    ctx = {
        'featured': featured,
        'latest': latest,
        'authors': authors,
        'posts': posts,
        'meta_title': f'{SITE_NAME} | فروشگاه اینترنتی خرید کتاب با ارسال سریع به سراسر ایران',
        'meta_description': (
            'پاتوق بوک، فروشگاه اینترنتی خرید کتاب: رمان، ادبیات کلاسیک، شعر، '
            'تاریخ و کتاب‌های تخفیف‌دار با قیمت مناسب و ارسال سریع به سراسر کشور.'
        ),
        'canonical_path': reverse('seo_pages:home'),
    }
    return render(request, 'seo_pages/home.html', ctx)


def _category_slug_map():
    """نگاشت نامک (slug) هر دسته‌بندی به متن واقعی‌اش، برای ساخت آدرس‌های
    مجزا و قابل ایندکس به‌جای پارامتر ?category= که قبلاً هیچ‌وقت به‌طور
    مستقل ایندکس نمی‌شد (چون canonical همیشه به /shop/ ساده اشاره می‌کرد)."""
    cats = Book.objects.exclude(category='').values_list('category', flat=True).distinct()
    return {slugify(c, allow_unicode=True): c for c in cats}


def _category_nav(slug_map, active_slug=''):
    return [
        {'slug': slug, 'name': name, 'active': slug == active_slug}
        for slug, name in sorted(slug_map.items(), key=lambda kv: kv[1])
    ]


def shop(request):
    books = Book.objects.select_related('author').filter(workshop=False)
    ctx = {
        'books': books,
        'categories': _category_nav(_category_slug_map()),
        'active_category': '',
        'meta_title': f'فروشگاه کتاب | {SITE_NAME}',
        'meta_description': _truncate(
            'فهرست همه‌ی کتاب‌های موجود برای خرید آنلاین ' + SITE_DESCRIPTION_SUFFIX
        ),
        'canonical_path': reverse('seo_pages:shop'),
    }
    return render(request, 'seo_pages/shop.html', ctx)


def shop_category(request, category_slug):
    """صفحه‌ی مجزا و قابل ایندکس برای هر دسته‌بندی، مثلاً /shop/category/رمان/
    تا عبارت‌هایی مثل «خرید کتاب رمان» بتوانند مستقل رتبه بگیرند."""
    slug_map = _category_slug_map()
    category = slug_map.get(category_slug)
    if not category:
        raise Http404('دسته‌بندی پیدا نشد')
    books = Book.objects.select_related('author').filter(workshop=False, category=category)
    ctx = {
        'books': books,
        'categories': _category_nav(slug_map, category_slug),
        'active_category': category,
        'meta_title': f'خرید کتاب {category} | {SITE_NAME}',
        'meta_description': _truncate(
            f'فهرست کتاب‌های دسته‌ی {category} برای خرید آنلاین ' + SITE_DESCRIPTION_SUFFIX
        ),
        'canonical_path': reverse('seo_pages:shop_category', args=[category_slug]),
    }
    return render(request, 'seo_pages/shop.html', ctx)


def book_detail(request, slug):
    book = get_object_or_404(Book.objects.select_related('author'), slug=slug)
    related = (
        Book.objects.select_related('author')
        .filter(category=book.category)
        .exclude(id=book.id)[:6]
    )
    ctx = {
        'book': book,
        'related': related,
        'meta_title': f'خرید کتاب {book.title} | {book.author.name} | {SITE_NAME}',
        'meta_description': _book_meta_description(book),
        'canonical_path': reverse('seo_pages:book_detail', args=[book.slug]),
    }
    return render(request, 'seo_pages/book_detail.html', ctx)


def authors_list(request):
    authors = Author.objects.all()
    ctx = {
        'authors': authors,
        'meta_title': f'نویسندگان | {SITE_NAME}',
        'meta_description': _truncate(f'فهرست نویسندگانی که کتاب‌هایشان {SITE_DESCRIPTION_SUFFIX}'),
        'canonical_path': reverse('seo_pages:authors_list'),
    }
    return render(request, 'seo_pages/authors.html', ctx)


def author_detail(request, slug):
    author = get_object_or_404(Author, slug=slug)
    books = Book.objects.filter(author=author)
    ctx = {
        'author': author,
        'books': books,
        'meta_title': f'کتاب‌های {author.name} | {SITE_NAME}',
        'meta_description': _author_meta_description(author),
        'canonical_path': reverse('seo_pages:author_detail', args=[author.slug]),
    }
    return render(request, 'seo_pages/author_detail.html', ctx)


def workshops(request):
    books = Book.objects.select_related('author').filter(workshop=True)
    ctx = {
        'books': books,
        'meta_title': f'کارگاه‌ها و محصولات آموزشی | {SITE_NAME}',
        'meta_description': _truncate(f'محصولات و کارگاه‌های آموزشی {SITE_DESCRIPTION_SUFFIX}'),
        'canonical_path': reverse('seo_pages:workshops'),
    }
    return render(request, 'seo_pages/workshops.html', ctx)


def library(request):
    pdfs = PdfItem.objects.filter(published=True)
    podcasts = Podcast.objects.filter(published=True).prefetch_related('episodes')
    ctx = {
        'pdfs': pdfs,
        'podcasts': podcasts,
        'meta_title': f'کتابخانه‌ی رسانه (پی‌دی‌اف و پادکست رایگان) | {SITE_NAME}',
        'meta_description': _truncate(f'دانلود رایگان پی‌دی‌اف و پادکست‌های صوتی {SITE_DESCRIPTION_SUFFIX}'),
        'canonical_path': reverse('seo_pages:library'),
    }
    return render(request, 'seo_pages/library.html', ctx)


def blog_list(request):
    posts = Post.objects.filter(published=True)
    ctx = {
        'posts': posts,
        'meta_title': f'وبلاگ | {SITE_NAME}',
        'meta_description': _truncate(f'مطالب و یادداشت‌های وبلاگ {SITE_DESCRIPTION_SUFFIX}'),
        'canonical_path': reverse('seo_pages:blog_list'),
    }
    return render(request, 'seo_pages/blog_list.html', ctx)


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    ctx = {
        'post': post,
        'meta_title': f'{post.title} | وبلاگ {SITE_NAME}',
        'meta_description': _truncate(post.content),
        'canonical_path': reverse('seo_pages:blog_detail', args=[post.slug]),
    }
    return render(request, 'seo_pages/blog_detail.html', ctx)


STORE_ADDRESS = 'نور، خیابان نیما، نبش نیلوفر ۴۳'
STORE_PHONE_DISPLAY = '۰۹۱۲۰۷۶۰۱۱۶'
STORE_PHONE_E164 = '+989120760116'
STORE_EMAIL = 'info@patoghebook.ir'
# کد پستی واقعی شعبه‌ی نور رو همین‌جا بین کوتیشن‌ها بنویس (مثلاً '4634617894')
# تا هم در JSON-LD (schema.org PostalAddress) و هم در صفحات درباره‌ما/تماس نمایش
# داده شود؛ تا وقتی خالی است این خط به‌طور خودکار نادیده گرفته می‌شود.
STORE_POSTAL_CODE = ''
# شنبه تا پنجشنبه ۹ تا ۲۱، جمعه تعطیل
STORE_HOURS_DISPLAY = 'شنبه تا پنج‌شنبه، ساعت ۹ تا ۲۱ — جمعه‌ها تعطیل'
_MAPS_QUERY = quote('نور خیابان نیما نبش نیلوفر ۴۳')
STORE_MAPS_EMBED_SRC = f'https://www.google.com/maps?q={_MAPS_QUERY}&output=embed'
STORE_MAPS_LINK = f'https://www.google.com/maps/search/?api=1&query={_MAPS_QUERY}'


def about(request):
    ctx = {
        'meta_title': f'درباره ما | {SITE_NAME}',
        'meta_description': _truncate(
            'پاتوق بوک یک کتاب‌فروشی اینترنتی با شعبه‌ی فیزیکی در شهر نور (مازندران) است؛ '
            f'داستان ما، آدرس و راه‌های ارتباطی {SITE_DESCRIPTION_SUFFIX}'
        ),
        'canonical_path': reverse('seo_pages:about'),
        'address': STORE_ADDRESS,
        'phone_display': STORE_PHONE_DISPLAY,
        'phone_e164': STORE_PHONE_E164,
        'email': STORE_EMAIL,
        'hours': STORE_HOURS_DISPLAY,
        'maps_embed_src': STORE_MAPS_EMBED_SRC,
        'maps_link': STORE_MAPS_LINK,
    }
    return render(request, 'seo_pages/about.html', ctx)


def contact(request):
    ctx = {
        'meta_title': f'تماس با ما | {SITE_NAME}',
        'meta_description': _truncate(
            f'آدرس، تلفن، ایمیل و ساعات کاری کتاب‌فروشی پاتوق بوک در نور (مازندران)؛ '
            f'پشتیبانی سفارش‌ها برای رشت و گیلان هم از همین راه‌های ارتباطی در دسترس است.'
        ),
        'canonical_path': reverse('seo_pages:contact'),
        'address': STORE_ADDRESS,
        'phone_display': STORE_PHONE_DISPLAY,
        'phone_e164': STORE_PHONE_E164,
        'email': STORE_EMAIL,
        'hours': STORE_HOURS_DISPLAY,
        'maps_embed_src': STORE_MAPS_EMBED_SRC,
        'maps_link': STORE_MAPS_LINK,
    }
    return render(request, 'seo_pages/contact.html', ctx)


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Disallow: /api/',
        'Disallow: /app/',
        '',
        f"Sitemap: {request.build_absolute_uri(reverse('seo_pages:sitemap'))}",
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


def sitemap_xml(request):
    # هر ورودی: (مسیر, تاریخ آخرین تغییر یا None, اولویت نسبی, بازه‌ی تغییر تقریبی)
    entries = [
        (reverse('seo_pages:home'), None, '1.0', 'daily'),
        (reverse('seo_pages:shop'), None, '0.9', 'daily'),
        (reverse('seo_pages:authors_list'), None, '0.6', 'weekly'),
        (reverse('seo_pages:workshops'), None, '0.6', 'weekly'),
        (reverse('seo_pages:library'), None, '0.6', 'weekly'),
        (reverse('seo_pages:blog_list'), None, '0.7', 'daily'),
        (reverse('seo_pages:about'), None, '0.5', 'monthly'),
        (reverse('seo_pages:contact'), None, '0.5', 'monthly'),
    ]
    for category_slug in _category_slug_map():
        entries.append((
            reverse('seo_pages:shop_category', args=[category_slug]),
            None, '0.7', 'daily',
        ))
    for book in Book.objects.all():
        entries.append((
            reverse('seo_pages:book_detail', args=[book.slug]),
            getattr(book, 'updated_at', None),
            '0.8', 'weekly',
        ))
    for author in Author.objects.all():
        entries.append((reverse('seo_pages:author_detail', args=[author.slug]), None, '0.5', 'monthly'))
    for post in Post.objects.filter(published=True):
        entries.append((
            reverse('seo_pages:blog_detail', args=[post.slug]),
            getattr(post, 'created_at', None),
            '0.6', 'monthly',
        ))

    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, lastmod, priority, changefreq in entries:
        body.append('<url>')
        body.append(f'<loc>{request.build_absolute_uri(path)}</loc>')
        if lastmod:
            body.append(f'<lastmod>{lastmod.date().isoformat()}</lastmod>')
        body.append(f'<changefreq>{changefreq}</changefreq>')
        body.append(f'<priority>{priority}</priority>')
        body.append('</url>')
    body.append('</urlset>')
    return HttpResponse('\n'.join(body), content_type='application/xml; charset=utf-8')
