from django.db import models
from django.utils.translation import ugettext_lazy as _

from .base import BaseModel


class AuthMethod(BaseModel):
    '''Model representing a single authentication method in an authentication service'''
    name = models.CharField(verbose_name=_('name'), default='', max_length=200)
    amr = models.CharField(
        help_text=_('id of the authentication method'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('Authentication method')
        verbose_name_plural = _('Authentication methods')

    def __str__(self):
        return f'{self.name} ({self.amr})'
