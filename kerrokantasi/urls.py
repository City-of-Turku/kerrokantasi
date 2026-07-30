from nested_admin import urls as nested_admin_urls
from django.conf import settings
from django.urls import include, re_path
from django.urls import path
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from democracy import urls_v1
from democracy.views.upload import browse, upload

from helusers.admin_site import admin

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'', include('helusers.urls')),
    re_path('', include('social_django.urls', namespace='social')),
    re_path(r'^v1/', include(urls_v1)),
    re_path(r'^nested_admin/', include(nested_admin_urls)),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^upload/', staff_member_required(upload), name='ckeditor_upload'),
    re_path(r'^browse/', never_cache(staff_member_required(browse)), name='ckeditor_browse'),
    path('', RedirectView.as_view(url='v1/'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
