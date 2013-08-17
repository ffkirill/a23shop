from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from django.core.management import call_command

from settings import ZIPFILE_SUPPORT
from settings import MAX_FILE_SIZE
from settings import UPLOAD_PATH, UPLOAD_DIR
from settings import PRICE_ID
from settings import CURRENCY_ID

import os

from utils import do_cleanup
from utils import extract_zipfile_uploads
from utils import check_upload_path

def process_checkauth(request):
    """Returns auth status and session id to store in cookie
    """
    return HttpResponse("Success\n"
                        "sessionid\n" +
                        request.COOKIES['sessionid'])


def process_init(request):
    """
    Performs cleanup
    Returns service options
    """
    do_cleanup()
    return HttpResponse("zip={0}\n"
                        "file_limit={1}".format('yes' if ZIPFILE_SUPPORT else 'no',
                                                MAX_FILE_SIZE))


def handle_uploaded_file(filename, path, data):
    """Stores uploaded file and extracts zipped file
    """
    with open(filename, 'ab') as destination:
        destination.write(data)

    # if os.path.splitext(filename)[1].lower() == '.zip':
    #     extract_zipfile(file, path)


def process_file(request):
    """Stores raw post data in file of 'filename' query GET value
     """
    filename = os.path.join(UPLOAD_PATH,
                            request.GET['filename'])

    check_upload_path()

    handle_uploaded_file(filename,
                         UPLOAD_PATH,
                         request.raw_post_data)

    return HttpResponse('success')


def process_import(request):
    """Executes import from xml file
    Currently process: 'import.xml' - Products data
                       'offers.xml' - Products prices data
    """
    extract_zipfile_uploads()

    filename = request.GET['filename'].lower()

    if 'import' in filename:

        call_command("custom_import",
                     os.path.join(UPLOAD_DIR, filename),
                     clear=False)

        return HttpResponse('success')

    elif 'offers' in filename:

        call_command("custom_import_offers",
                     os.path.join(UPLOAD_DIR, filename),
                     price_id=None,
                     currency=CURRENCY_ID)

        return HttpResponse('success')

    else:

        return HttpResponse('failure')

def process_clear(request):
    """Clears catalog
    """
    call_command("custom_clearcatalog")
    return HttpResponse('success')

@csrf_exempt
@permission_required("manage_shop", login_url="/login/")
def process(request):
    """
    Main exchange view. Emulates 1cbitrix api.
    """

    mode = request.GET.get("mode")

    if mode == "checkauth":
        return process_checkauth(request)

    elif mode == "init":
        return process_init(request)

    elif mode == "file":
        return process_file(request)

    elif mode == "import":
        return process_import(request)

    elif mode == "clear":
        return process_clear(request)

    else:
        return HttpResponseBadRequest('/')
