"""
WSGI config for kerrokantasi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import logging
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kerrokantasi.settings")

application = get_wsgi_application()

try:
    from kerrokantasi.oidc_cache import warm_oidc_cache

    warm_oidc_cache()
except Exception:
    logging.getLogger(__name__).warning(
        'Failed to warm OIDC JWKS cache at startup',
        exc_info=True,
    )
