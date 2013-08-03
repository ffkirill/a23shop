# -*- coding: utf-8 -*-
from django.conf import settings
import os

ZIPFILE_SUPPORT = True
MAX_FILE_SIZE = 1 * 1024 * 1024
UPLOAD_DIR = 'upload'
UPLOAD_PATH = os.path.normpath(os.path.join(settings.DIRNAME, '1cbitrix', UPLOAD_DIR))
PRICE_ID = '55da4af6-f57c-11de-82d3-001e8c1a8cef'
CURRENCY_ID = u'руб'