import os

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from django.utils.html import format_html_join

from media_library.validators import IMAGE_EXTENSION_VALIDATOR, validate_image_size

from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'id']
    search_fields = ['name']
    readonly_fields = ['slug']


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """A FileField whose widget accepts several files at once (standard
    Django pattern for multi-file uploads since ClearableFileInput gained
    `allow_multiple_selected`)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(d, initial) for d in data if d]
        return single_clean(data, initial)


class BookAdminForm(forms.ModelForm):
    new_images = MultipleFileField(
        required=False,
        label='آپلود عکس جدید',
        help_text='یک یا چند عکس انتخاب کن؛ به تصاویر فعلی این کتاب اضافه می‌شوند.',
        # SECURITY: without this, save_model() below took the extension
        # straight from whatever filename the browser sent (os.path.splitext)
        # and wrote the file into MEDIA_ROOT/book_covers/ with that same
        # extension, unchecked — an admin could upload a .html/.svg/.php file
        # that a misconfigured web server might later execute or that a
        # browser would render (rather than download) if opened directly.
        validators=[IMAGE_EXTENSION_VALIDATOR, validate_image_size],
    )
    clear_existing_images = forms.BooleanField(
        required=False,
        label='حذف همه‌ی عکس‌های قبلی این کتاب',
    )

    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            # The raw JSON list is still editable manually if needed, but is
            # no longer the primary way to manage images.
            'images': forms.Textarea(attrs={'rows': 2}),
        }


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm
    list_display = ['title', 'slug', 'author', 'price', 'discount', 'stock', 'category', 'featured', 'category2', 'workshop', 'created_at']
    list_filter = ['category', 'featured', 'category2', 'workshop']
    search_fields = ['title', 'author__name']
    autocomplete_fields = ['author']
    readonly_fields = ['current_images_preview', 'slug']
    fields = [
        'title', 'slug', 'author', 'price', 'discount', 'category', 'category2',
        'workshop', 'stock', 'emoji', 'featured', 'description',
        'current_images_preview', 'images', 'new_images', 'clear_existing_images',
    ]

    def current_images_preview(self, obj):
        # SECURITY: this used to build the whole <img> markup as one plain
        # f-string (with `url` interpolated raw) and then hand it to
        # format_html() with no placeholder args. format_html() only escapes
        # values passed as *arguments* — called this way it just marks the
        # whole pre-built string safe, identical to mark_safe(), so any
        # quote/HTML character inside an image URL would break out of the
        # attribute and inject arbitrary markup/script into the admin page
        # (stored XSS, since `images` can contain manually-typed URLs — see
        # the raw JSON Textarea widget above). Building the tag through
        # format_html's own "{}"-placeholder substitution (one call per
        # image) makes each url go through Django's normal auto-escaping.
        if not obj or not obj.pk or not obj.images:
            return 'هنوز عکسی ثبت نشده.'
        return format_html_join(
            '',
            '<img src="{}" style="height:90px;margin:4px;border:1px solid #ccc;border-radius:6px;">',
            ((url,) for url in obj.images),
        )
    current_images_preview.short_description = 'عکس‌های فعلی'

    def save_model(self, request, obj, form, change):
        clear_existing = form.cleaned_data.get('clear_existing_images')
        new_files = form.cleaned_data.get('new_images') or []

        if clear_existing:
            obj.images = []

        super().save_model(request, obj, form, change)

        if new_files:
            media_dir = os.path.join(settings.MEDIA_ROOT, 'book_covers')
            os.makedirs(media_dir, exist_ok=True)
            urls = list(obj.images or [])
            for f in new_files:
                ext = os.path.splitext(f.name)[1] or '.jpg'
                filename = f'book_covers/{obj.id}_{get_random_string(6)}{ext}'
                saved_path = default_storage.save(filename, f)
                urls.append(f'{settings.MEDIA_URL}{saved_path}')
            obj.images = urls
            obj.save(update_fields=['images'])
