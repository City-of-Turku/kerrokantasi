# -*- coding: utf-8 -*-
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib import admin

from .models import User

class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {'fields': ('uuid', 'nickname')}),
    )

admin.site.register(User, UserAdmin)
