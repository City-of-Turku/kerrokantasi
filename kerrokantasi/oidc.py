import json

import requests
from django.conf import settings
from django.utils import timezone
from helusers.oidc import ApiTokenAuthentication as HelApiTokenAuth
from requests.exceptions import RequestException
from rest_framework.exceptions import AuthenticationFailed


class ApiTokenAuthentication(HelApiTokenAuth):
    def authenticate(self, request):
        try:
            result = super().authenticate(request)
        except json.JSONDecodeError as exc:
            raise AuthenticationFailed(
                'Unable to verify access token: authentication service returned an invalid response.'
            ) from exc
        except RequestException as exc:
            raise AuthenticationFailed(
                'Unable to verify access token: authentication service is temporarily unavailable.'
            ) from exc

        if result is None:
            return None

        user, auth = result
        payload = auth.data

        if not user.is_staff and payload.get('aud') == settings.KERROKANTASI_MOD_TOOL_CLIENT_ID:
            raise AuthenticationFailed()

        if payload.get('amr') in settings.STRONG_AUTH_PROVIDERS:
            user.has_strong_auth = True
        else:
            user.has_strong_auth = False

        user.last_login = timezone.now()
        user.notified_about_expiration = False
        user.save()
        return user, auth
