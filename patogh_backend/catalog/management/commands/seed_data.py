from django.core.management.base import BaseCommand

from blog.models import Post
from catalog.models import Author, Book


class Command(BaseCommand):
    help = 'Loads the same starter books/posts the original localStorage version shipped with.'

    def handle(self, *args, **options):
        if Book.objects.exists():
            self.stdout.write(self.style.WARNING('کتاب‌ها از قبل وجود دارند؛ چیزی اضافه نشد.'))
            return

        books = [
            ('بوف کور', 'صادق هدایت', 180000, 0, 'ادبیات کلاسیک', '📖', 12),
            ('کیمیاگر', 'پائولو کوئیلو', 220000, 15, 'رمان', '🌟', 8),
            ('صد سال تنهایی', 'گابریل گارسیا مارکز', 260000, 0, 'رمان', '🦋', 5),
            ('تاریخ ایران باستان', 'حسن پیرنیا', 340000, 10, 'تاریخ', '🏛️', 6),
            ('مثنوی معنوی', 'مولانا', 280000, 0, 'شعر', '🕊️', 10),
            ('جنگ و صلح', 'لئو تولستوی', 390000, 20, 'رمان', '⚔️', 4),
        ]
        for title, author_name, price, discount, category, emoji, stock in books:
            author, _ = Author.objects.get_or_create(name=author_name)
            Book.objects.create(
                title=title, author=author, price=price, discount=discount,
                category=category, emoji=emoji, featured=True, stock=stock,
            )

        posts = [
            ('۵ کتاب برتر برای شروع کتاب‌خوانی',
             'اگر تازه می‌خواهید کتاب‌خوانی را شروع کنید، انتخاب کتاب اول اهمیت زیادی دارد. '
             'در این مطلب چند پیشنهاد ساده و جذاب برای شروع آورده‌ایم که خواندن را به یک عادت '
             'لذت‌بخش تبدیل می‌کند.'),
            ('چرا باید کتاب کاغذی بخوانیم؟',
             'در دنیای دیجیتال امروز، کتاب کاغذی همچنان جایگاه ویژه‌ای دارد. لمس کاغذ، بوی '
             'صفحات و تمرکز بیشتر هنگام مطالعه، از مزایای کتاب چاپی نسبت به نسخه دیجیتال است.'),
        ]
        for title, content in posts:
            Post.objects.create(title=title, content=content)

        self.stdout.write(self.style.SUCCESS('داده‌های اولیه با موفقیت بارگذاری شدند.'))
