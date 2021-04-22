from nested_admin import urls as nested_admin_urls
from django.conf import settings
from django.urls import path, re_path
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from democracy import urls_v1
from democracy.views.upload import browse, upload
from django.views.generic.base import RedirectView
from django.http import HttpResponseRedirect
from helusers.admin_site import admin
from django.contrib.auth import logout as django_logout

def redirect(request):
    django_logout(request)
    return HttpResponseRedirect(settings.ADMIN_LOGOUT_REDIRECT or '/')


urlpatterns = [
    path('admin/logout/', redirect),
    url(r'^admin/', admin.site.urls),
    url(r'', include('helusers.urls')),
    url('', include('social_django.urls', namespace='social')),
    url(r'^v1/', include(urls_v1)),
    url(r'^nested_admin/', include(nested_admin_urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^upload/', staff_member_required(upload), name='ckeditor_upload'),
    url(r'^browse/', never_cache(staff_member_required(browse)), name='ckeditor_browse'),
    path('', RedirectView.as_view(url='v1/'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
