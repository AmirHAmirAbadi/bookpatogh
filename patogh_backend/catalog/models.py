from django.db import models

from patogh_backend.idgen import generate_id


class Author(models.Model):
    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    name = models.CharField('نام نویسنده', max_length=200, unique=True)
    bio = models.TextField('بیوگرافی', blank=True, default='')

    class Meta:
        verbose_name = 'نویسنده'
        verbose_name_plural = 'نویسندگان'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    title = models.CharField('عنوان', max_length=300)
    author = models.ForeignKey(Author, verbose_name='نویسنده', related_name='books', on_delete=models.CASCADE)
    price = models.PositiveIntegerField('قیمت (تومان)', default=0)
    discount = models.PositiveSmallIntegerField('تخفیف (٪)', default=0)
    category = models.CharField('دسته‌بندی', max_length=120, default='عمومی')
    category2 = models.BooleanField('کتاب دسته ۲', default=False)
    stock = models.PositiveIntegerField('موجودی انبار', default=0)
    emoji = models.CharField('ایموجی جلد', max_length=10, default='📚', blank=True)
    images = models.JSONField('تصاویر', default=list, blank=True)
    featured = models.BooleanField('پیشنهاد ویژه', default=False)
    description = models.TextField('توضیحات', blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'کتاب'
        verbose_name_plural = 'کتاب‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def cover(self):
        return self.images[0] if self.images else None

    @property
    def final_price(self):
        if self.discount:
            return round(self.price * (1 - self.discount / 100))
        return self.price
