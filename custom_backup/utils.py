import os
import shutil
import zipfile

import time

from itertools import chain

from settings import *
from django.conf import settings

DATABASES = settings.DATABASES


def do_mysql_backup(database_name,
                    outfile,
                    username=None,
                    password=None,
                    host=None,
                    port=None):
    """
    Performs mysql backup
    """
    args = []

    if username:
        args += ["--user='{0}'".format(username)]
    if password:
        args += ["--password='{0}'".format(password)]
    if host:
        args += ["--host='{0}'".format(host)]
    if port:
        args += ["--port={0}".format(port)]

    args += [database_name]

    os.system('{0} {1} > {2}'.format(
        SQLDUMP_COMMAND,
        ' '.join(args),
        outfile))


def do_postgresql_backup(database_name,
                         outfile,
                         username=None,
                         password=None,
                         host=None,
                         port=None):
    """
    Performs postresql backup
    """
    args = []
    if username:
        args += ["--username={0}".format(username)]
    if host:
        args += ["--host={0}".format(host)]
    if port:
        args += ["--port={0}".format(port)]

    args += [database_name]

    if password:
        os.environ['PGPASSWORD'] = password

    os.system('{0} {1} --clean > {2}'.format(
        PGDUMP_COMMAND,
        ' '.join(args),
        outfile))


def do_sqlite_backup(database_name,
                     outfile,
                     username=None,
                     password=None,
                     host=None,
                     port=None):
    """
    Performs sqlite backup
    """
    shutil.copyfile(database_name, outfile)


DB_ENGINE_HANDLERS = {
    'django.db.backends.postgresql_psycopg2': do_postgresql_backup,
    'django.db.backends.mysql' : do_mysql_backup,
    'django.db.backends.sqlite3': do_sqlite_backup,
    'django.db.backends.oracle': None
}


def zip_directory(path, zipobj):
    """
    Creates zip archive from directory
    """
    for root, dirs, files in os.walk(path):
        for file in files:

            for exclude_path in EXCLUDE_DIRS:
                if os.path.normpath(root).startswith(exclude_path):
                    continue

            if os.path.normpath(root).startswith(BACKUP_PATH):
                continue

            zipobj.write(os.path.join(root, file))


def check_backup_dir():
    """
    Creates backup dir if it does not exist
    """
    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH, 0755)


def perform_backup():
    """
    Creates zipped dump of databases in settings
    """
    db_files = []

    #Create db dumps
    for db_key, db_settings in chain(
            DATABASES.iteritems(),
            APPEND_DATABASES.iteritems()):
        ENGINE = db_settings.get('ENGINE')
        db_backup_handler = DB_ENGINE_HANDLERS.get(ENGINE)

        database_name = db_settings.get('NAME')
        username = db_settings.get('USER')
        password = db_settings.get('PASSWORD')
        host = db_settings.get('HOST')
        port = db_settings.get('PORT')

        check_backup_dir()

        outfile = os.path.join(BACKUP_PATH, db_key) + '.db'

        if db_backup_handler:
            db_backup_handler(database_name, outfile,
                    username=username,
                    password=password,
                    host=host,
                    port=port)
            db_files.append(outfile)
        else:
            print "No backup handler for ENGINE {0}.\n"
            "Backup is not complete".format(ENGINE)

    #Create destination zipfile
    zipfile_name = os.path.join(
        BACKUP_PATH,
        time.strftime(TIME_FORMAT) + '.zip')

    with zipfile.ZipFile(zipfile_name, 'w') as destination:

        for filename in db_files:
            destination.write(filename)

        for path in APPEND_DIRS:
            zip_directory(path, destination)

    return zipfile_name