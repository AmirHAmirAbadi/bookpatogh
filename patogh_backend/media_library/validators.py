"""
SECURITY: FileField uploads had no extension or size validation at all —
even though only staff can reach these endpoints (IsAdminOrReadOnly), an
admin session (or a hijacked/CSRF'd one) could still upload something like
`shell.php`, `virus.exe`, or a multi-GB file. `FileExtensionValidator` limits
what *kind* of file can be stored, and `validate_file_size` puts a hard cap
on how big it can be, regardless of who is uploading.

Extension checks are not a perfect defense (content can still lie about
its own type), but they close off the easy cases and keep whatever the web
server in front of MEDIA_ROOT serves restricted to the expected file kinds.
"""
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

PDF_EXTENSION_VALIDATOR = FileExtensionValidator(allowed_extensions=['pdf'])
IMAGE_EXTENSION_VALIDATOR = FileExtensionValidator(
    allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif']
)
AUDIO_EXTENSION_VALIDATOR = FileExtensionValidator(
    allowed_extensions=['mp3', 'wav', 'ogg', 'm4a']
)

MAX_PDF_SIZE = 50 * 1024 * 1024      # 50MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024    # 10MB
MAX_AUDIO_SIZE = 200 * 1024 * 1024   # 200MB


def _validate_max_size(value, max_bytes, label):
    if value.size > max_bytes:
        raise ValidationError(
            f'حجم فایل {label} بیش از حد مجاز است (حداکثر {max_bytes // (1024 * 1024)} مگابایت).'
        )


def validate_pdf_size(value):
    _validate_max_size(value, MAX_PDF_SIZE, 'PDF')


def validate_image_size(value):
    _validate_max_size(value, MAX_IMAGE_SIZE, 'عکس')


def validate_audio_size(value):
    _validate_max_size(value, MAX_AUDIO_SIZE, 'صوتی')
