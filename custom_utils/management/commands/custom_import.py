# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from xml.etree import ElementTree

from custom_utils.utils import update_category_entry
from custom_utils.utils import update_product_entry
import lfs_additional_categories.models

import os

from settings import DIRNAME

from custom_utils.settings import PRODUCTS_PATH_SUBDIR

from optparse import make_option

import lfs_solr
import lfs_solr.utils

XML_ROOT_TAG = u'КоммерческаяИнформация'
CATEGORIES_XPATH = u'Классификатор/Группы/Группа'
ADDITIONAL_CATEGORIES_XPATH = u'Классификатор/СМ_ЦеновыеГруппы/Группы/Группа'
PRODUCTS_XPATH = u'Каталог/Товары/Товар'


class Command(BaseCommand):
    args = '<file1.xml file2.xml..>'
    help = 'Imports catalog information from xmls stored in 1cbitrix'
    option_list = BaseCommand.option_list + (
        make_option('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clears whole catalog before import'),
        )

    def handle(self, *args, **options):

        lfs_solr.disconnect()

        if options['clear']:
            from custom_utils.management.commands.custom_clearcatalog import Command as ClearCommand
            clear_cmd = ClearCommand()
            clear_cmd.handle()

        for arg in args:
            path = os.path.join(DIRNAME, PRODUCTS_PATH_SUBDIR, arg)
            print 'Importing {0}...'.format(path)
            tree = ElementTree.parse(path)
            root = tree.getroot()

            if root.tag != XML_ROOT_TAG:
                print('Invalid xml file format')
                return

            categories = root.findall(CATEGORIES_XPATH)
            for category in categories:
                update_category_entry(category)

            additional_categories = root.findall(ADDITIONAL_CATEGORIES_XPATH)
            for category in additional_categories:
                update_category_entry(category, Category=lfs_additional_categories.models.AdditionalCategory)

            products  = root.findall(PRODUCTS_XPATH)
            for product in products:
                update_product_entry(product)



        print 'Recreating indices..'
        lfs_solr.utils.index_products()
        lfs_solr.connect()
        print 'Done.'