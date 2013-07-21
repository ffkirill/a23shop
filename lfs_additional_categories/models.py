from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from lfs.core.fields.thumbs import ImageWithThumbsField
from lfs.catalog.models import Product
from lfs.catalog.models import StaticBlock

# django imports
from django import forms
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from lfs.catalog.models import VARIANT
from lfs.catalog.models import Category

# portlets imports
from portlets.models import Portlet

# lfs imports
import lfs.catalog.utils


import uuid

from settings import ADDITIONAL_CATEGORY_SESSION_KEY

def get_unique_id_str():
    return str(uuid.uuid4())


class AdditionalCategory(models.Model):
    """

    """
    name = models.CharField(_(u"Name"), max_length=50)
    slug = models.SlugField(_(u"Slug"), unique=True)
    parent = models.ForeignKey("self", verbose_name=_(u"Parent"), blank=True, null=True)

    products = models.ManyToManyField(Product, verbose_name=_(u"Products"), blank=True, related_name="additional_categories")
    short_description = models.TextField(_(u"Short description"), blank=True)
    description = models.TextField(_(u"Description"), blank=True)
    image = ImageWithThumbsField(_(u"Image"), upload_to="images", blank=True, null=True, sizes=((60, 60), (100, 100), (200, 200), (400, 400)))
    position = models.IntegerField(_(u"Position"), default=1000)

    static_block = models.ForeignKey(StaticBlock, verbose_name=_(u"Static block"), blank=True, null=True, related_name="additional_categories")

    level = models.PositiveSmallIntegerField(default=1)
    uid = models.CharField(max_length=50, editable=False, unique=True, default=get_unique_id_str)

    class Meta:
        ordering = ("position", )
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.slug)

    def get_absolute_url(self):
        """
        Returns the absolute_url.
        """
        return ("lfs.catalog.views.category_view", (), {"slug": self.slug})
    get_absolute_url = models.permalink(get_absolute_url)

    @property
    def content_type(self):
        """
        Returns the content type of the category as lower string.
        """
        return u"additional_category"

    def get_all_children(self):
        """
        Returns all child categories of the category.
        """
        def _get_all_children(category, children):
            for category in AdditionalCategory.objects.filter(parent=category.id):
                children.append(category)
                _get_all_children(category, children)

        cache_key = "%s-additional-category-all-children-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        children = cache.get(cache_key)
        if children is not None:
            return children

        children = []
        for category in AdditionalCategory.objects.filter(parent=self.id):
            children.append(category)
            _get_all_children(category, children)

        cache.set(cache_key, children)
        return children

    def get_children(self):
        """
        Returns the first level child categories.
        """
        cache_key = "%s-additional-category-children-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)

        categories = cache.get(cache_key)
        if categories is not None:
            return categories

        categories = AdditionalCategory.objects.filter(parent=self.id)
        cache.set(cache_key, categories)

        return categories


    def get_image(self):
        """
        Returns the image of the category if it has none it inherits that from
        the parent category.
        """
        if self.image:
            return self.image
        else:
            if self.parent:
                return self.parent.get_image()

        return None

    def get_parents(self):
        """
        Returns all parent categories.
        """
        cache_key = "%s-additional-category-parents-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        parents = cache.get(cache_key)
        if parents is not None:
            return parents

        parents = []
        category = self.parent
        while category is not None:
            parents.append(category)
            category = category.parent

        cache.set(cache_key, parents)
        return parents


    def get_products(self):
        """
        Returns the direct products and all products of the sub categories
        """
        cache_key = "%s-additional-category-all-products-%s" % (settings.CACHE_MIDDLEWARE_KEY_PREFIX, self.id)
        products = cache.get(cache_key)
        if products is not None:
            return products

        categories = [self]
        categories.extend(self.get_all_children())

        products = lfs.catalog.models.Product.objects.distinct().filter(
            active=True,
            additional_categories__in=categories).exclude(sub_type=VARIANT).distinct()

        cache.set(cache_key, products)
        return products



class AdditionalFilterPortlet(Portlet):
    """A portlet to display filters.
    """
    default_category = models.ForeignKey(Category, verbose_name=_(u"Default category"))


    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        request = context.get("request")

        category = context.get("category")

        if category is None:
            category = self.default_category

        # get saved filters
        additional_category_id = request.session.get(ADDITIONAL_CATEGORY_SESSION_KEY)
        if additional_category_id:
            try:
                additional_category = AdditionalCategory.objects.get(pk=additional_category_id)
            except:
                del request.session[ADDITIONAL_CATEGORY_SESSION_KEY]
                additional_category = AdditionalCategory()
        else:
            additional_category = AdditionalCategory()


        if additional_category.pk:
            path = additional_category.get_parents()[::-1]
            path.append(additional_category)
            choice_items = additional_category.get_children()
        else:
            path = []
            choice_items = AdditionalCategory.objects.filter(level=1).order_by("name")

        return render_to_string("lfs_additional_categories/caterories_filter.html", RequestContext(request, {
            "show": True,
            "title": self.title,
            "category": category,
            "path": path,
            "choice_items": choice_items,
        }))

    def form(self, **kwargs):
        return FilterPortletForm(instance=self, **kwargs)


class FilterPortletForm(forms.ModelForm):
    """Form for the FilterPortlet.
    """
    class Meta:
        model = AdditionalFilterPortlet
