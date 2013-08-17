# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from xml.etree import ElementTree
import os

from django.conf import settings
from ...settings import PRODUCTS_PATH_SUBDIR

from optparse import make_option

import lfs_solr

from lfs.catalog.models import Product

_XML_ROOT_TAG = u'КоммерческаяИнформация'
_PRICE_TYPE_XPATH = u"ПакетПредложений/ТипыЦен/ТипЦены[1]"
_OFFERS_XPATH_TEMPLATE = u"ПакетПредложений/Предложения/Предложение"
_PRICES_XPATH_TEMPLATE = u"Цены/Цена[ИдТипаЦены='{0}'][Валюта='{1}']"


def get_price_type_id(xml_root):
    """
    Returns default (first) price type id in xml
    """
    price_type_entry = xml_root.find(_PRICE_TYPE_XPATH)
    if price_type_entry:
        return price_type_entry.find(u"Ид").text


def _set_price_for_product(product_uid, unit, price):
    product = Product.objects.get(uid=product_uid)
    product.price = price
    product.unit = unit
    product.save()


class Command(BaseCommand):
    args = '<file1.xml file2.xml..>'
    help = 'Imports offers information from xmls stored in 1cbitrix'
    option_list = BaseCommand.option_list + (

        make_option('-p', '--price-id',
                    action='store',
                    dest='price_id',
                    default=None,
                    help='Price category uid'),

        make_option('-c', '--currency',
                    action='store',
                    dest='currency',
                    default=u'руб',
                    help='Currency name'),
    )

    def handle(self, *args, **options):

        lfs_solr.disconnect()

        for arg in args:

            path = os.path.join(settings.DIRNAME, PRODUCTS_PATH_SUBDIR, arg)
            print(path)
            print 'Importing {0}...'.format(path)

            tree = ElementTree.parse(path)
            root = tree.getroot()

            if root.tag != _XML_ROOT_TAG:
                print('Invalid xml file format')
                return

            price_type_id = options['price_id'] or get_price_type_id(root)

            offers = root.findall(_OFFERS_XPATH_TEMPLATE)

            for offer_entry in offers:
                prices = offer_entry.findall(_PRICES_XPATH_TEMPLATE.format(
                    price_type_id,
                    options['currency'],
                ))

                for price_entry in prices:
                    uid = offer_entry.find(u'Ид').text
                    unit = price_entry.find(u'Единица').text
                    price = float(price_entry.find(u'ЦенаЗаЕдиницу').text)
                    _set_price_for_product(uid, unit, price)

        lfs_solr.connect()

