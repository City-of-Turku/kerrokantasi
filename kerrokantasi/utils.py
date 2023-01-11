from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

import logging



logger = logging.getLogger(__name__)


def send_mail(*, address, subject, body, **kwargs):
    """
    Send an email to the given address.\n
    kwargs:
        attachments: list of (filename, content) tuples
        html: rendered html body
    """
    if not settings.EMAIL_ENABLED:
        logger.info('(Code: 21) Email is disabled.')
        return
    try:
        attachments = kwargs.get('attachments', None)
        html = kwargs.get('html', None)
        mail_from = settings.DEFAULT_FROM_EMAIL or 'noreply@%s' % Site.objects.get_current().domain
        email = EmailMultiAlternatives(subject, body, mail_from, to=[address], attachments=attachments)
        if html:
            email.attach_alternative(html, 'text/html')
        email.send()
    except:
        logger.error('(Code: 32) Failed to send mail.')