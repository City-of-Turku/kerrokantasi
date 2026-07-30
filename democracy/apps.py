# -*- coding: utf-8 -*-
from django.apps.config import AppConfig
from django.utils.translation import gettext_lazy as _


class DemocracyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'democracy'
    verbose_name = _("Participatory Democracy")

    def ready(self):
        from . import signals
