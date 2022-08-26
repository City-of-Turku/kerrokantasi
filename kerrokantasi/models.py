from datetime import datetime, timedelta
from django.db import models
from helusers.models import AbstractUser

from kerrokantasi.utils import send_mail
from django.utils.translation import ugettext as _


class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True)
    has_strong_auth = models.BooleanField(default=False)
    notified_about_expiration = models.BooleanField(default=False)

    def __str__(self):
        return ' - '.join([super().__str__(), self.get_display_name(), self.email])

    def get_real_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name).strip()

    def get_display_name(self):
        return self.nickname or self.get_real_name()

    def get_default_organization(self):
        return self.admin_organizations.order_by('created_at').first()

    def get_has_strong_auth(self):
        return self.has_strong_auth

    def send_expiration_notification(self):
        if not self.email or not self.admin_organizations.exists():
            return
        msg = f"{_('Kerrokantasi account will expire %(date)s.') % ({'date': (datetime.now() + timedelta(days=30)).date().strftime('%d.%m.%Y')})}\n" + \
              f"{_('You must login to the service before the expiration date to prevent account removal.')}" + \
              f"\n\n{_('Best regards, Kerrokantasi')}"
        send_mail(address=self.email, subject=_('Kerrokantasi account expiration'), body=msg)