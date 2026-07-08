from django.db import models  # noqa: F401

# This app intentionally has no custom models. Both regular customers and the
# store admin are plain django.contrib.auth.User records:
#   - username        -> the phone number (or email) the person signs up with
#   - first_name       -> their display name
#   - is_staff=True    -> grants access to the admin-only write endpoints
#                          (create the first one with `python manage.py createsuperuser`)
