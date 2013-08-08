import os
import zipfile

from glob import iglob
import shutil

from settings import *


def do_cleanup():
    """
    Deletes everything at upload path
    """
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_PATH)
    check_upload_path()


def check_upload_path():
    """
    Creates directory for upload
    """
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH, 0755)


def extract_zipfile(filename, path):
    """
    Extracts zipfile named 'filename' into 'path'.
    Original file will be removed
    """
    with zipfile.ZipFile(filename, 'r') as destination:
        destination.extractall(path)
    os.remove(filename)


def extract_multipart_zip_upload():
    """
    Extracts multipart upload at upload path.
    Original file parts will be removed
    """
    parts = sorted(iglob(MULTIPART_ZIPFILE_PATTERN))

    for filename in parts:
        destination = os.path.splitext(filename)[0]
        with open(destination, 'wb') as destination_obj:
            with open(filename, 'rb') as part_obj:
                shutil.copyfileobj(part_obj, destination_obj)
            os.remove(filename)
        extract_zipfile(destination, UPLOAD_PATH)


def extract_zipfile_uploads():
    """
    Extracts zipped uploads at upload path,
    and then, removes original zip files
    """
    for filename in iglob(os.path.join(UPLOAD_PATH, '*.zip')):
        extract_zipfile(filename, UPLOAD_PATH)