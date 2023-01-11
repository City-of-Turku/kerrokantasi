from django.db.models.signals import m2m_changed
from democracy.models.organization import Organization, OrganizationLog
from kerrokantasi.models import User
from django.utils.translation import gettext_lazy as _



def organization_log_signal(sender, **kwargs):
    instance = kwargs.get('instance', None)
    action = kwargs.get('action')
    pk_set = kwargs.get('pk_set')
    if any(isinstance(_id, str) for _id in pk_set):
        return
    users = User.objects.filter(pk__in=pk_set)
    if action == 'post_add':
        OrganizationLog.objects.create(
            organization=instance,
            action=_('Added: %(email)s') % ({ 'email': ', '.join([user.email for user in users]) }),
            action_by=instance.modified_by
        )
    elif action == 'post_remove':
        OrganizationLog.objects.create(
            organization=instance,
            action=_('Removed: %(email)s') % ({ 'email': ', '.join([user.email for user in users]) }),
            action_by=instance.modified_by
        )

m2m_changed.connect(organization_log_signal, sender=Organization.admin_users.through)