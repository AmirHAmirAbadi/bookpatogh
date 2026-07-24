"""
اتصال به درگاه پرداخت زرین‌پال (Zarinpal).

این ماژول دو کار را با خودِ سرور زرین‌پال انجام می‌دهد (هر دو server-to-server،
یعنی هیچ‌کدام‌شان از مرورگر کاربر رد نمی‌شوند):

1. request_payment(...)   مرحله‌ی اول: گرفتن یک «Authority» یک‌بارمصرف برای مبلغ
                          دقیق همین سفارش. بعد از این، خودِ مرورگرِ کاربر (نه
                          سرور) به آدرس StartPay/{authority} هدایت می‌شود تا وارد
                          صفحه‌ی واقعی پرداخت زرین‌پال شود.
2. verify_payment(...)    مرحله‌ی آخر: بعد از برگشت کاربر از زرین‌پال، پیش از
                          این که سفارش را «پرداخت‌شده» علامت بزنیم، از خودِ
                          زرین‌پال می‌پرسیم که آیا این تراکنش واقعاً و قطعاً
                          موفق بوده یا نه. هرگز فقط بر اساس پارامترهای برگشتی
                          در URL به بانک اعتماد نمی‌کنیم؛ چون آن‌ها از مرورگر
                          کاربر می‌آیند و قابل جعل هستند.

آدرس‌های زیر آدرس‌های رسمی و ثابتِ درگاه زرین‌پال هستند (مستقل از پذیرنده) و
تغییر نمی‌کنند؛ چیزی که برای هر پذیرنده فرق می‌کند فقط «کد پذیرنده»
(Merchant ID) است که در تنظیمات «اتصال» پنل ادمین ذخیره می‌شود.
"""
import logging

import requests

logger = logging.getLogger(__name__)

REQUEST_URL = 'https://api.zarinpal.com/pg/v4/payment/request.json'
VERIFY_URL = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
START_PAY_URL = 'https://www.zarinpal.com/pg/StartPay/{authority}'

REQUEST_TIMEOUT = 15  # ثانیه


class ZarinpalError(Exception):
    """هر خطای قابل‌نمایش به کاربر هنگام صحبت با سرور زرین‌پال (شبکه، تایم‌اوت، یا خطای خودِ زرین‌پال)."""


def request_payment(merchant_id, amount_rial, description, callback_url, mobile=''):
    """
    مرحله‌ی «PaymentRequest». amount_rial باید مبلغ به *ریال* باشد (زرین‌پال
    ریال می‌خواهد، نه تومان) و از روی Order.total که خودِ سرور محاسبه کرده
    ساخته می‌شود؛ هیچ‌وقت از داده‌ی مرورگر گرفته نمی‌شود.

    خروجی: رشته‌ی authority در صورت موفقیت.
    خطا: ZarinpalError با پیام قابل‌نمایش، در صورت هر مشکلی.
    """
    payload = {
        'merchant_id': merchant_id,
        'amount': int(amount_rial),
        'description': description,
        'callback_url': callback_url,
    }
    if mobile:
        payload['metadata'] = {'mobile': mobile}

    try:
        resp = requests.post(REQUEST_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error('Zarinpal PaymentRequest failed: %s', exc)
        raise ZarinpalError('ارتباط با درگاه پرداخت زرین‌پال برقرار نشد. لطفاً کمی بعد دوباره تلاش کنید.') from exc
    except ValueError as exc:  # پاسخ JSON نامعتبر
        logger.error('Zarinpal PaymentRequest returned invalid JSON: %s', resp.text[:500])
        raise ZarinpalError('پاسخ نامعتبر از درگاه پرداخت زرین‌پال دریافت شد.') from exc

    result = data.get('data') or {}
    errors = data.get('errors') or {}
    code = result.get('code')
    authority = result.get('authority')

    if code != 100 or not authority:
        msg = None
        if isinstance(errors, dict):
            msg = errors.get('message')
        logger.warning('Zarinpal PaymentRequest rejected: %s', data)
        raise ZarinpalError(msg or 'درخواست پرداخت زرین‌پال رد شد.')

    return authority


def verify_payment(merchant_id, amount_rial, authority):
    """
    مرحله‌ی «PaymentVerification»: تنها منبع قابل‌اعتماد برای این‌که بگوییم پول
    واقعاً از کارت مشتری کم شده یا نه. همیشه باید قبل از ست‌کردن
    Order.payment_status = 'paid' فراخوانی شود.

    خروجی: dict شامل حداقل کلید 'success' (bool). در صورت موفقیت، کلید
    'ref_id' (شماره پیگیری تراکنش زرین‌پال) هم در dict قرار می‌گیرد.
    """
    payload = {
        'merchant_id': merchant_id,
        'amount': int(amount_rial),
        'authority': authority,
    }
    try:
        resp = requests.post(VERIFY_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error('Zarinpal PaymentVerification request failed: %s', exc)
        return {'success': False, 'raw': None, 'error': str(exc)}
    except ValueError as exc:
        logger.error('Zarinpal PaymentVerification returned invalid JSON: %s', resp.text[:500])
        return {'success': False, 'raw': None, 'error': str(exc)}

    result = data.get('data') or {}
    code = result.get('code')
    # کد 100: تراکنش برای اولین بار تایید شد. کد 101: قبلاً هم تایید شده بود
    # (idempotent؛ تراکنش هنوز موفق محسوب می‌شود، فقط دوباره verify نشده).
    success = code in (100, 101)

    out = {'success': success, 'raw': data}
    if success and result.get('ref_id') is not None:
        out['ref_id'] = result.get('ref_id')
    return out
