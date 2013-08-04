# -*- coding: utf-8 -*-
from django.contrib import contenttypes

import lfs.catalog.models
from lfs.catalog.models import Product
from lfs.catalog.models import Image
from django.conf import settings
import lfs_additional_categories

DIRNAME = settings.DIRNAME

import os
from custom_utils.settings import PRODUCTS_PATH_SUBDIR
from django.core.files import File

from pytils.translit import slugify

XML_TO_DJANGO_MAP = {'name': u'Наименование',
                     'uid': u'Ид'}

CATEGORY_TAG = u'Группы/Группа'
PRODUCT_CATEGORIES_TAG = u'Группы/Ид'
PRODUCT_ADDITIONAL_CATEGORY_TAG = u'СМ_ЦеноваяГруппа/Ид'
PRODUCT_PICTURE_TAG = u'Картинка'

import logging

logger = logging.getLogger("default")


def slug_make_unique(slug, item, increment=0):
    manager = item.__class__.objects

    slug_calculated = slug + '-' + str(increment) if increment else slug

    if not manager.filter(slug=slug_calculated).exclude(pk=item.pk).count():
        return slug_calculated

    count = manager.filter(slug__startswith=slug_calculated).exclude(pk=item.pk).count()

    increment += 1
    return slug_make_unique(slug, item, count + increment)


def save_image_for_product(product, path):
    image = Image(content=product, title=path)
    with open(os.path.join(DIRNAME, PRODUCTS_PATH_SUBDIR, path), 'rb') as file:
        try:
            f = File(file)
            image.image.save(file.name, content=f, save=True)
        except Exception, e:
            logger.info("Upload image: %s %s" % (file.name, e))


def update_category_entry(element, parent=None, level=1,
                          Category=lfs.catalog.models.Category):
    uid_field = XML_TO_DJANGO_MAP['uid']
    name_field = XML_TO_DJANGO_MAP['name']

    uid_value = element.find(uid_field).text[:49]
    name_value = element.find(name_field).text[:49]

    if not parent and Category == lfs.catalog.models.Category:
        try:
            parent = Category.objects.get(slug="all")
        except Category.DoesNotExist:
            parent = Category.objects.create(name=u"Товары",
                                             slug="all",
                                             level=1,
                                             template=1)
        level = 2

    try:
        item = Category.objects.get(uid=uid_value)
    except Category.DoesNotExist:
        item = Category()
        item.uid = uid_value

    slug_value = slugify(name_value[:30])

    if not slug_value in item.slug:
        slug_value = slug_make_unique(slug_value, item)
        item.slug = slug_value[:49]

    item.name = name_value
    item.level = level
    item.parent = parent
    item.save()

    subelements = element.findall(CATEGORY_TAG)
    for subelement in subelements:
        update_category_entry(subelement, item, level + 1, Category)


def update_product_entry(element):
    uid_field = XML_TO_DJANGO_MAP['uid']
    name_field = XML_TO_DJANGO_MAP['name']

    if element.find(uid_field) is None or element.find(name_field) is None:
        return

    uid_value = element.find(uid_field).text
    name_value = element.find(name_field).text[:79]

    try:
        item = Product.objects.get(uid=uid_value)
    except Product.DoesNotExist:
        item = Product()
        item.uid = uid_value
        item.sku = uid_value[:29]

    slug_value = slugify(name_value[:65])

    if not slug_value in item.slug:
        slug_value = slug_make_unique(slug_value, item)
        item.slug = slug_value

    item.active = True
    item.name = name_value
    item.save()

    item_categories = element.findall(PRODUCT_CATEGORIES_TAG)
    item.categories.clear()

    for category_entry in item_categories:
        category = lfs.catalog.models.Category.objects.get(uid=category_entry.text)
        item.categories.add(category)

    picture_entry = element.find(PRODUCT_PICTURE_TAG)
    if picture_entry is not None:
        save_image_for_product(item, picture_entry.text)

    additional_category_entry = element.find(PRODUCT_ADDITIONAL_CATEGORY_TAG)
    if additional_category_entry is not None:
        additional_category = lfs_additional_categories.models.AdditionalCategory.objects.get(
            uid=additional_category_entry.text
        )
        item.additional_categories.add(additional_category)

    item.save()