from django.conf import settings
from django.utils import translation
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta


User = get_user_model()

class Command(BaseCommand):
    def handle(self, **options):
        about_to_expire = User.objects.filter(
            last_login__lte=datetime.now() - timedelta(days=settings.USER_EXPIRATION_DAYS - 30)
        )
        has_expired = about_to_expire.filter(
            last_login__lte=datetime.now() - timedelta(days=settings.USER_EXPIRATION_DAYS)
        )
        about_to_expire = about_to_expire.exclude(
            pk__in=has_expired.values_list('pk', flat=True)
        )

        with translation.override(settings.LANGUAGES[0][0]):
            for user in about_to_expire.filter(notified_about_expiration=False):
                user.send_expiration_notification()
                user.notified_about_expiration = True
                user.save()

        has_expired.delete()
