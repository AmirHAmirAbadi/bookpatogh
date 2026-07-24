"""
سربرگ‌ها و فرم ورودِ پیش‌فرض پنل ادمین جنگو («Django administration» و لیبل
فیلد یوزرنیم) به‌صراحت اسم «جنگو» را نشان می‌دهند و از فناوری پشتِ سایت خبر
می‌دهند. این فایل همان چیزها را با متن فارسیِ خنثی جایگزین می‌کند، بدون این‌که
هیچ رفتار امنیتی/عملکردیِ صفحه‌ی ورود تغییر کند (همان بررسی رمز، همان CSRF،
همان throttle که در accounts هست دست‌نخورده می‌ماند — این فقط ظاهر است).
"""
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm

# --- سربرگ‌های پنل ---------------------------------------------------------
admin.site.site_header = 'پنل مدیریت پاتوق بوک'
admin.site.site_title = 'پاتوق بوک'
admin.site.index_title = 'مدیریت فروشگاه'


# --- لیبل فیلدهای فرم ورود --------------------------------------------------
class BrandedAdminAuthenticationForm(AdminAuthenticationForm):
    """همان فرم استاندارد ورودِ ادمین، فقط با لیبل فارسیِ خنثی برای دو فیلد،
    به‌جای چیزی که ممکن است هویت جنگو را لو بدهد."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'نام کاربری'
        self.fields['password'].label = 'رمز عبور'


admin.site.login_form = BrandedAdminAuthenticationForm
admin.site.login_template = None  # همان قالب پیش‌فرض کافی است؛ فقط محتوای فرم عوض شده
