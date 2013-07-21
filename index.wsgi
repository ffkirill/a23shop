import locale
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
sys.path.insert(0, PROJECT_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()