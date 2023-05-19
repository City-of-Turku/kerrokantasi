from helusers.oidc import ApiTokenAuthentication as HelApiTokenAuth, AuthenticationFailed
from django.conf import settings
from django.utils import timezone

class ApiTokenAuthentication(HelApiTokenAuth):
    def __init__(self, *args, **kwargs):
        super(ApiTokenAuthentication, self).__init__(*args, **kwargs)

    def authenticate(self, request):
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None
        
        payload = self.decode_jwt(jwt_value)
        user, auth = super(ApiTokenAuthentication, self).authenticate(request)

        if not user.is_staff and payload.get('aud') == settings.KERROKANTASI_MOD_TOOL_CLIENT_ID:
            raise AuthenticationFailed()

        # amr (Authentication Methods References) should contain the used auth 
        # provider name e.g. suomifi
        if payload.get('amr') in settings.STRONG_AUTH_PROVIDERS:
            user.has_strong_auth = True
        else:
            user.has_strong_auth = False

        user.last_login = timezone.now()
        user.notified_about_expiration = False
        user.save()
        return (user, auth)
    
    def get_audiences(self, api_token):
        return self.settings.AUDIENCE