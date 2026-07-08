"""
Shared helper to generate short string IDs, mirroring the original
frontend's `uid()` function (id + 7 random base36 chars), so records
created by Django keep the same ID "shape" the JS code expects
(e.g. book.id === 'idab12xyz').
"""
from django.utils.crypto import get_random_string

ID_ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'


def generate_id():
    return 'id' + get_random_string(7, allowed_chars=ID_ALPHABET)


def generate_order_no():
    """PBxxxxxx order numbers, same format the frontend used to fake client-side."""
    from orders.models import Order  # local import avoids circular import at app load time
    while True:
        candidate = 'PB' + get_random_string(6, allowed_chars='0123456789')
        if not Order.objects.filter(id=candidate).exists():
            return candidate
