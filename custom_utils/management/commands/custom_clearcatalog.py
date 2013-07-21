# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


def _raw_clear_table(model):
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute('DELETE FROM "{0}"'.format(model._meta.db_table))
    for m2m_field in model._meta._many_to_many():
        table_name = m2m_field.m2m_db_table()
        cursor.execute('DELETE FROM "{0}"'.format(table_name))
        print(table_name)


class Command(BaseCommand):
    args = ''
    help = 'Deletes products and categories'


    def handle(self, *args, **options):
        print 'Clear catalog model tables:'
        from django.db import transaction
        from lfs.catalog import models as catalog_models
        from lfs_additional_categories import models as additional_cat_models

        import inspect
        from django.db.models import Model
        from lfs.portlet.models import Portlet

        all_models = {'lfs.catalog.models': catalog_models,
                      'lfs_additional_categories.models': additional_cat_models,
                      }

        for _name, _model in all_models.iteritems():
            print _name, _model
            for item in (item for item in _model.__dict__.values()
                         if inspect.isclass(item) and issubclass(item, Model)
                         and not issubclass(item, Portlet)
                         and item.__module__ == _name
            ):
                _raw_clear_table(item)
                print item

        transaction.commit_unless_managed()
        print 'Done.'
