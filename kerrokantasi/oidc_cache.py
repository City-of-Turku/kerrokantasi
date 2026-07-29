import logging

logger = logging.getLogger(__name__)


def warm_oidc_cache():
    """
    Fetch Tunnistamo JWKS once at startup.

    helusers 1.x caches signing keys in-process. With many uWSGI workers, the
    first request on each worker otherwise triggers its own outbound fetch to
    testitunnistamo, which can fail intermittently and surface as 500 errors.
    """
    from django.conf import settings
    from helusers.oidc import get_keys

    issuer = settings.OIDC_API_TOKEN_AUTH.get('ISSUER')
    if not issuer:
        return

    issuers = [issuer] if isinstance(issuer, str) else issuer
    for iss in issuers:
        if not iss:
            continue
        get_keys(iss)
        logger.info('Warmed OIDC JWKS cache for issuer %s', iss)
