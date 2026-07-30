import os

from PIL import Image
from ckeditor_uploader.backends import get_backend
from ckeditor_uploader.forms import SearchForm
from ckeditor_uploader.views import get_files_browse_urls
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.views import generic

from ckeditor_uploader.utils import storage
from democracy.views.section import RootFileSerializer


class AbsoluteUrlImageUploadView(generic.View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        """
        Uploads a file and send back its URL to CKEditor.

        Based on django-ckeditor's ImageUploadView, but stores files in
        protected storage and returns absolute serve_file URLs.
        """
        uploaded_file = request.FILES['upload']
        backend = get_backend()
        ck_func_num = escape(request.GET['CKEditorFuncNum'])

        filewrapper = backend(storage, uploaded_file)
        allow_nonimages = getattr(settings, 'CKEDITOR_ALLOW_NONIMAGE_FILES', True)
        if not filewrapper.is_image and not allow_nonimages:
            return HttpResponse("""
                <script type='text/javascript'>
                window.parent.CKEDITOR.tools.callFunction({0}, '', 'Invalid file type.');
                </script>""".format(ck_func_num))

        section_file = self._save_file(request, uploaded_file)
        if section_file is None:
            return HttpResponse("""
                <script type='text/javascript'>
                window.parent.CKEDITOR.tools.callFunction({0}, '', 'Upload failed.');
                </script>""".format(ck_func_num))

        url = reverse('serve_file', kwargs={'filetype': 'sectionfile', 'pk': section_file.pk})
        url = request.build_absolute_uri(url)

        return HttpResponse("""
        <script type='text/javascript'>
            window.parent.CKEDITOR.tools.callFunction({0}, '{1}');
        </script>""".format(ck_func_num, url))

    @staticmethod
    def _save_file(request, uploaded_file):
        """
        Uploaded files are saved to the protected storage.
        """
        serializer = RootFileSerializer(data={'file': uploaded_file}, context={})
        if not serializer.is_valid():
            return None
        section_file_obj = serializer.save()

        filename = section_file_obj.file.path
        img_name, img_format = os.path.splitext(filename)
        image_quality = getattr(settings, "IMAGE_QUALITY", 60)
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS

        if str(img_format).lower() == "png":
            img = Image.open(section_file_obj.file.path)
            img = img.resize(img.size, resample)
            img.save("{}.jpg".format(img_name), quality=image_quality, optimize=True)
            section_file_obj.file.name = section_file_obj.file.name.replace('.png', '.jpg')
            section_file_obj.file.save()
        elif str(img_format).lower() in ("jpg", "jpeg"):
            img = Image.open(uploaded_file)
            img = img.resize(img.size, resample)
            img.save(section_file_obj.file.path, quality=image_quality, optimize=True)

        return section_file_obj


upload = csrf_exempt(AbsoluteUrlImageUploadView.as_view())


def browse(request):
    """
    Uploaded file browse view with absolute URLs for CKEditor.
    """
    files = get_files_browse_urls(request.user)

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('q', '').lower()
            files = list(filter(lambda d: query in d['visible_filename'].lower(), files))
    else:
        form = SearchForm()

    show_dirs = getattr(settings, 'CKEDITOR_BROWSE_SHOW_DIRS', False)
    dir_list = sorted(set(os.path.dirname(f['src']) for f in files), reverse=True)

    if os.name == 'nt':
        files = [f for f in files if os.path.basename(f['src']) != 'Thumbs.db']

    for f in files:
        f['src'] = request.build_absolute_uri(f['src'])

    context = {
        'show_dirs': show_dirs,
        'dirs': dir_list,
        'files': files,
        'form': form
    }
    return render(request, 'ckeditor/browse.html', context)
