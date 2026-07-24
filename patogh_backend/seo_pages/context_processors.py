from . import views


def store_info(request):
    """کد پستی (و در آینده هر مقدار سراسری دیگر) رو در اختیار همه‌ی
    قالب‌ها می‌گذارد، از جمله base.html که روی همه‌ی صفحات رندر می‌شود."""
    return {
        'store_postal_code': views.STORE_POSTAL_CODE,
    }
