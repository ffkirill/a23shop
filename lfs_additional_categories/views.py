from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from settings import ADDITIONAL_CATEGORY_SESSION_KEY
import utils

from lfs.catalog.views import lfs_get_object_or_404
from lfs.catalog.views import Category
from lfs.catalog.views import CONTENT_PRODUCTS
# from lfs.catalog.views import category_categories
from lfs.catalog.views import render_to_response
from lfs.catalog.views import RequestContext
from lfs.catalog.views import settings
from lfs.catalog.views import Paginator
from lfs.catalog.views import cache
from lfs.catalog.views import lfs_pagination
from lfs.catalog.views import render_to_string
from lfs.catalog.views import EmptyPage, InvalidPage

import lfs.catalog.utils


def reset_filter(request, category_slug):
    """Resets all product filter. Redirects to the category with given slug.
    """
    if ADDITIONAL_CATEGORY_SESSION_KEY in request.session:
        del request.session[ADDITIONAL_CATEGORY_SESSION_KEY]

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def set_filter(request, category_slug, additional_category_id=0):
    """Saves the given filter to session. Redirects to the category with given
    slug.
    """
    request.session[ADDITIONAL_CATEGORY_SESSION_KEY] = additional_category_id

    url = reverse("lfs_category", kwargs={"slug": category_slug})
    return HttpResponseRedirect(url)


def category_products(request, slug, start=1,
                      template_name="lfs/catalog/categories/product/default.html"):
    """Displays the products of the category with passed slug.

    This view is called if the user chooses a template that is situated in settings.PRODUCT_PATH ".
    """
    # Resets the product filters if the user navigates to another category.
    # TODO: Is this what a customer would expect?
    last_category = request.session.get("last_category")
    if (last_category is None) or (last_category.slug != slug):
        if "product-filter" in request.session:
            del request.session["product-filter"]
        if "price-filter" in request.session:
            del request.session["price-filter"]

    try:
        default_sorting = settings.LFS_PRODUCTS_SORTING
    except AttributeError:
        default_sorting = "price"
    sorting = request.session.get("sorting", default_sorting)

    product_filter = request.session.get("product-filter", {})
    product_filter = product_filter.items()
    additional_filter = request.session.get(ADDITIONAL_CATEGORY_SESSION_KEY)

    cache_key = "%s-category-products-%s" % (
    settings.CACHE_MIDDLEWARE_KEY_PREFIX, slug)
    sub_cache_key = "%s-start-%s-sorting-%s" % (
    settings.CACHE_MIDDLEWARE_KEY_PREFIX, start, sorting)

    filter_key = ["%s-%s" % (i[0], i[1]) for i in product_filter]
    if filter_key:
        sub_cache_key += "-%s" % "-".join(filter_key)
    if additional_filter:
        sub_cache_key += "-%s" % "-".join(additional_filter)

    price_filter = request.session.get("price-filter")
    if price_filter:
        sub_cache_key += "-%s-%s" % (price_filter["min"], price_filter["max"])

    temp = cache.get(cache_key)
    if temp is not None:
        try:
            return temp[sub_cache_key]
        except KeyError:
            pass
    else:
        temp = dict()

    category = lfs_get_object_or_404(Category, slug=slug)

    # Calculates parameters for display.
    try:
        start = int(start)
    except (ValueError, TypeError):
        start = 1

    format_info = category.get_format_info()
    amount_of_rows = format_info["product_rows"]
    amount_of_cols = format_info["product_cols"]
    amount = amount_of_rows * amount_of_cols

    all_products = lfs.catalog.utils.get_filtered_products_for_category(
        category, product_filter, price_filter, sorting)

    additional_filter_result_is_empty = False
    if additional_filter:
        all_products_filtered = utils.get_filtered_products_for_additional_filter(
            all_products, additional_filter)

        if not all_products_filtered.count() and all_products.count():
            additional_filter_result_is_empty = True
        else:
            all_products = all_products_filtered

    # prepare paginator
    paginator = Paginator(all_products, amount)

    try:
        current_page = paginator.page(start)
    except (EmptyPage, InvalidPage):
        current_page = paginator.page(paginator.num_pages)

    # Calculate products
    row = []
    products = []
    for i, product in enumerate(current_page.object_list):
        if product.is_product_with_variants():
            default_variant = product.get_variant_for_category(request)
            if default_variant:
                product = default_variant

        image = None
        product_image = product.get_image()
        if product_image:
            image = product_image.image
        row.append({
            "obj": product,
            "slug": product.slug,
            "name": product.get_name(),
            "image": image,
            "price_unit": product.price_unit,
            "price_includes_tax": product.price_includes_tax(request),
        })
        if (i + 1) % amount_of_cols == 0:
            products.append(row)
            row = []

    if len(row) > 0:
        products.append(row)

    amount_of_products = all_products.count()

    # Calculate urls
    pagination_data = lfs_pagination(request, current_page,
                                     url=category.get_absolute_url())

    render_template = category.get_template_name()
    if render_template != None:
        template_name = render_template

    result = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "products": products,
        "amount_of_products": amount_of_products,
        "pagination": pagination_data,
        "all_products": all_products,
        "additional_filter_result_is_empty": additional_filter_result_is_empty,
    }))

    temp[sub_cache_key] = result
    cache.set(cache_key, temp)
    return result


def category_categories(request, slug, start=0,
                        template_name="lfs/catalog/categories/category/default.html"):
    """Displays the child categories of the category with passed slug.

    This view is called if the user chooses a template that is situated in settings.CATEGORY_PATH ".
    """
    cache_key = "%s-category-categories-%s" % (
    settings.CACHE_MIDDLEWARE_KEY_PREFIX, slug)

    result = cache.get(cache_key)
    if result is not None:
        return result

    category = lfs_get_object_or_404(Category, slug=slug)

    format_info = category.get_format_info()
    amount_of_cols = format_info["category_cols"]

    categories = []
    row = []
    for i, children in enumerate(category.get_children()):
        row.append(children)
        if (i + 1) % amount_of_cols == 0:
            categories.append(row)
            row = []

    if len(row) > 0:
        categories.append(row)

    result = render_to_string(template_name, RequestContext(request, {
        "category": category,
        "categories": categories,
    }))

    cache.set(cache_key, result)
    return result


def lfs_category_hook(request, slug,
                      template_name="lfs/catalog/category_base.html"):
    """
    """
    start = request.REQUEST.get("start", 1)
    category = lfs_get_object_or_404(Category, slug=slug)

    if category.get_content() == CONTENT_PRODUCTS:
        categories_inline = category_categories(request, slug,
                                                template_name='lfs/catalog/categories/category/inline.html')
        inline = category_products(request, slug, start)
    else:
        categories_inline = ""
        inline = category_categories(request, slug)
        # Set last visited category for later use, e.g. Display breadcrumbs,
    # selected menu points, etc.
    request.session["last_category"] = category

    # TODO: Factor top_category out to a inclusion tag, so that people can
    # omit if they don't need it.

    return render_to_response(template_name, RequestContext(request, {
        "category": category,
        "categories_inline": categories_inline,
        "category_inline": inline,
        "top_category": lfs.catalog.utils.get_current_top_category(request,
                                                                   category),
    }))
