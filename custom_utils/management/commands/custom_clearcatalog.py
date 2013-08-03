# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
import lfs_solr
import lfs_solr.utils


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

        from lfs.catalog.models import Category, Product
        from lfs_additional_categories.models import AdditionalCategory

        try:
            lfs_solr.disconnect()
        except:
            pass

        for _model in (Product, Category, AdditionalCategory):
            while _model.objects.all().count():
                _model.objects.all()[0].delete()

        try:
            lfs_solr.utils.index_products()
            lfs_solr.connect()
        except:
            pass

        print 'Done.'
