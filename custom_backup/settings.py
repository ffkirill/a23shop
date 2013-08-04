import os
from django.conf import settings

SQLDUMP_COMMAND = 'mysqldump'
PGDUMP_COMMAND = 'pg_dump'

BACKUP_DIR = 'backup'
BACKUP_PATH = os.path.normpath(os.path.join(settings.DIRNAME,
                                            BACKUP_DIR))

APPEND_DIRS = [
    settings.DIRNAME
]

EXCLUDE_DIRS = [
    os.path.normpath(os.path.join(settings.DIRNAME,
                     '1cbitrix'))
]

APPEND_DATABASES = {}

TIME_FORMAT = '%Y%m%d-%H%M%S'

del os
del settings
