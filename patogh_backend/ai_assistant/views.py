import json
import urllib.error
import urllib.request

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

# Both providers are REST/JSON APIs, just with different shapes:
#  - xAI (Grok):    POST https://api.x.ai/v1/chat/completions            (OpenAI-compatible)
#  - Google Gemini: POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
XAI_CHAT_URL = 'https://api.x.ai/v1/chat/completions'
GEMINI_URL_TMPL = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'

SYSTEM_PROMPT = (
    'تو «دستیار هوش مصنوعی» پنل مدیریت فروشگاه اینترنتی کتاب «پاتوق بوک» هستی. '
    'وظیفه‌ات کمک به ادمین فروشگاه است: مدیریت سایت، نوشتن و ویرایش پست وبلاگ، '
    'پیشنهاد سئو و عنوان، و مشاوره درباره‌ی کتاب‌ها، کارگاه‌ها، پادکست‌ها و فایل‌های PDF. '
    'پاسخ‌ها را به زبان فارسی، مختصر، مؤدبانه و کاربردی بده.'
)

# How many turns of prior conversation to forward, to keep each request bounded.
MAX_HISTORY_MESSAGES = 20

SEO_SYSTEM_PROMPT = (
    'تو یک متخصص سئو (SEO) برای فروشگاه اینترنتی کتاب «پاتوق بوک» هستی. '
    'برای پست وبلاگی که ادمین می‌دهد (عنوان + متن)، این‌ها را پیشنهاد بده: '
    'یک عنوان بهینه‌شده برای سئو (optimized_title, حداکثر ۶۰ نویسه)، '
    'یک توضیحات متا (meta_description, حدود ۱۲۰ تا ۱۵۵ نویسه)، '
    'حدود ۵ تا ۸ کلمه‌ی کلیدی مرتبط (keywords, آرایه‌ای از رشته‌ها)، '
    'و ۳ تا ۵ پیشنهاد عملی برای بهبود متن از نظر سئو و خوانایی (suggestions, آرایه‌ای از رشته‌ها). '
    'پاسخ را **فقط** به‌صورت یک آبجکت JSON خام و معتبر با دقیقاً همین چهار کلید برگردان — '
    'بدون Markdown، بدون ```، بدون هیچ متن اضافه‌ی قبل یا بعد از JSON. '
    'همه‌ی متن‌ها باید فارسی باشند.'
)


class IsStaffUser(permissions.BasePermission):
    """Only the logged-in store admin (is_staff) may use the assistant —
    it is an internal tool, not a public-facing feature."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


def _clean_history(history):
    if not isinstance(history, list):
        return []
    cleaned = []
    for item in history[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role = item.get('role')
        content = item.get('content')
        if role in ('user', 'assistant') and content:
            cleaned.append({'role': role, 'content': str(content)[:4000]})
    return cleaned


def _send(req, provider_name):
    """Runs the request; returns the parsed JSON body, or a Persian error
    string (never raises) so callers can just check `isinstance(x, str)`."""
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode('utf-8', errors='ignore'))
            err_detail = err_body.get('error') or err_body
        except Exception:
            err_detail = f'HTTP {e.code}'
        return f'خطا از سمت {provider_name} (کد {e.code}): {err_detail}'
    except urllib.error.URLError as e:
        return f'عدم دسترسی به سرور {provider_name} (شبکه/اینترنت سرور را بررسی کن): {e.reason}'
    except Exception as e:
        return f'خطای غیرمنتظره در ارتباط با {provider_name}: {e}'


def _call_grok(history, message, system_prompt=None):
    api_key = settings.XAI_API_KEY
    if not api_key:
        return None, (
            'کلید XAI_API_KEY روی سرور تنظیم نشده. آن را در فایل .env قرار بده '
            '(XAI_API_KEY=...) و سرور جنگو را ری‌استارت کن.'
        )

    messages = [{'role': 'system', 'content': system_prompt or SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': message})

    payload = json.dumps({
        'model': settings.XAI_MODEL,
        'messages': messages,
        'temperature': 0.7,
    }).encode('utf-8')

    req = urllib.request.Request(
        XAI_CHAT_URL,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
    )
    body = _send(req, provider_name='Grok')
    if isinstance(body, str):
        return None, body
    try:
        return body['choices'][0]['message']['content'], None
    except (KeyError, IndexError, TypeError):
        return '', None


def _call_gemini(history, message, system_prompt=None):
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None, (
            'کلید GEMINI_API_KEY روی سرور تنظیم نشده. آن را در فایل .env قرار بده '
            '(GEMINI_API_KEY=...) و سرور جنگو را ری‌استارت کن.'
        )

    contents = []
    for item in history:
        # Gemini calls the assistant's role "model", not "assistant".
        role = 'model' if item['role'] == 'assistant' else 'user'
        contents.append({'role': role, 'parts': [{'text': item['content']}]})
    contents.append({'role': 'user', 'parts': [{'text': message}]})

    payload = json.dumps({
        'system_instruction': {'parts': [{'text': system_prompt or SYSTEM_PROMPT}]},
        'contents': contents,
    }).encode('utf-8')

    url = GEMINI_URL_TMPL.format(model=settings.GEMINI_MODEL)
    req = urllib.request.Request(
        url,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key,
        },
    )
    body = _send(req, provider_name='Gemini')
    if isinstance(body, str):
        return None, body
    try:
        return body['candidates'][0]['content']['parts'][0]['text'], None
    except (KeyError, IndexError, TypeError):
        return '', None


PROVIDERS = {
    'gemini': _call_gemini,
    'grok': _call_grok,
}


def _extract_json_object(text):
    """Models sometimes wrap JSON in ```json ... ``` fences or add stray
    text around it despite instructions; pull out the first {...} block
    and parse that instead of trusting the whole string to be clean JSON."""
    if not text:
        return None
    text = text.strip()
    if text.startswith('```'):
        text = text.strip('`')
        if text.lower().startswith('json'):
            text = text[4:]
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except (ValueError, TypeError):
        return None


class AIChatView(APIView):
    """POST /api/ai/chat/  { message, history }  ->  { reply }

    Proxies the admin panel's chat widget to whichever provider is set in
    AI_PROVIDER ('gemini' or 'grok' — see settings.py / .env). Both API keys
    live only in the server's environment — never sent to, or visible from,
    the browser.
    """

    permission_classes = [IsStaffUser]

    def post(self, request):
        message = (request.data.get('message') or '').strip()
        if not message:
            return Response({'detail': 'پیام نمی‌تواند خالی باشد.'}, status=status.HTTP_400_BAD_REQUEST)

        history = _clean_history(request.data.get('history'))

        provider = (settings.AI_PROVIDER or 'gemini').lower()
        call = PROVIDERS.get(provider, _call_gemini)

        reply, error = call(history, message)
        if error:
            return Response({'detail': error}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({'reply': reply or ''})


class AISeoView(APIView):
    """POST /api/ai/seo/  { title, content }  ->
    { optimized_title, meta_description, keywords: [...], suggestions: [...] }

    Used by the "✨ سئو با هوش مصنوعی" button in the admin blog editor.
    Same provider plumbing as AIChatView, just with a task-specific system
    prompt that asks the model to reply with a JSON object instead of a
    free-form chat reply.
    """

    permission_classes = [IsStaffUser]

    def post(self, request):
        title = (request.data.get('title') or '').strip()
        content = (request.data.get('content') or '').strip()
        if not title or not content:
            return Response(
                {'detail': 'عنوان و متن مطلب هر دو الزامی هستند.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = f'عنوان: {title}\n\nمتن:\n{content[:6000]}'

        provider = (settings.AI_PROVIDER or 'gemini').lower()
        call = PROVIDERS.get(provider, _call_gemini)

        raw, error = call([], message, system_prompt=SEO_SYSTEM_PROMPT)
        if error:
            return Response({'detail': error}, status=status.HTTP_502_BAD_GATEWAY)

        data = _extract_json_object(raw)
        if not data:
            return Response(
                {'detail': 'پاسخ هوش مصنوعی قابل تحلیل نبود؛ دوباره تلاش کن.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        keywords = data.get('keywords')
        suggestions = data.get('suggestions')
        return Response({
            'optimized_title': str(data.get('optimized_title') or '')[:200],
            'meta_description': str(data.get('meta_description') or '')[:300],
            'keywords': [str(k) for k in keywords][:12] if isinstance(keywords, list) else [],
            'suggestions': [str(s) for s in suggestions][:8] if isinstance(suggestions, list) else [],
        })
