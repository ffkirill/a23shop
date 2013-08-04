from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from utils import perform_backup
from django.core.servers.basehttp import FileWrapper
import os

@user_passes_test(lambda u: u.is_superuser, login_url="/login/")
def process(request):
    """
    Main view.
    """
    filename = perform_backup()
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(
        os.path.basename(filename))

    os.remove(filename)
    return response

