from django.http import HttpRequest

# pysolr imports
from pysolr import Solr

# lfs imports
from lfs.catalog.models import Product
from lfs.catalog.settings import STANDARD_PRODUCT
from lfs.catalog.settings import PRODUCT_WITH_VARIANTS
from lfs.catalog.settings import CONFIGURABLE_PRODUCT
from django.test.client import RequestFactory
try:
    SOLR_ADDRESS = settings.SOLR_ADDRESS
except:
    from lfs_solr.settings import SOLR_ADDRESS

def index_product(product):
    """Indexes passed product.
    """
    if product.is_variant():
        try:
            product = product.parent.get_default_variant()
        except AttributeError:
            return
    fr = RequestFactory()
    request = fr.get('/index-products')
    _index_products([product], request)


def delete_product(product):
    """Deletes passed product from index.
    """
    conn = Solr(SOLR_ADDRESS)
    conn.delete(id=product.id)
    
def index_all_products(request):
    """Indexes all products.
    """
    products = Product.objects.filter(
        active=True, sub_type__in = (STANDARD_PRODUCT, PRODUCT_WITH_VARIANTS, CONFIGURABLE_PRODUCT))

    _index_products(products, request, delete=True)

def index_products():
    """Indexes all product.
    """

    fr = RequestFactory()
    request = fr.get('/index-products')
    index_all_products(request)


def _index_products(products, request, delete=False):
    """Indexes given products.
    """
    conn = Solr(SOLR_ADDRESS)
    if delete:
        conn.delete(q='*:*')

    temp = []
    for product in products:

        # Just index the default variant of a "Product with Variants"
        if product.is_product_with_variants():
            product = product.get_default_variant()

        if product is None:
            continue

        # Categories
        categories = []
        for category in product.get_categories():
            categories.append(category.name)

        # Manufacturer
        manufacturer = product.manufacturer
        if manufacturer:
            manufacturer_name = manufacturer.name
        else:
            manufacturer_name = ""

        temp.append({
            "id" : product.id,
            "name" : product.get_name(),
            "price" : product.get_price(request),
            "categories" : categories,
            "keywords" : product.get_meta_keywords(),
            "manufacturer" : manufacturer_name,
            "sku_manufacturer" : product.sku_manufacturer,
            "description" : product.description,
        })

    conn.add(temp)