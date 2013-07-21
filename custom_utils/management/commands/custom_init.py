# -*- coding: utf-8 -*-

# django imports
from django.core.management.base import BaseCommand
from django.conf import settings

SHOP_DESCRIPTION = u"""
<h1 class="first-heading">Добро пожаловать в LFS!</h1>
<p>LFS - интернет-магазин, основанный на <a href="http://www.python.org/" target="_blank">Python</a>,
<a href="http://www.djangoproject.com/" target="_blank">Django</a> and
<a href="http://jquery.com/" target="_blank">jQuery</a>.</p>

<h1>Вход</h1>
<p>Перейдите к <a href="/manage">управлению</a> для начала добавления контента.</p>

<h1>Информация &amp; Help</h1>
<p>Источники дополнительной информации:</p>
<ul>
<li><a href="http://www.getlfs.com" target="_blank">Официальная страница разработчика</a></li>
<li><a href="http://packages.python.org/django-lfs/index.html" target="_blank">Документация на PyPI</a></li>
<li><a href="http://pypi.python.org/pypi/django-lfs" target="_blank">Релизы на PyPI</a></li>
<li><a href="http://bitbucket.org/diefenbach/django-lfs" target="_blank">Исходный код на bitbucket.org</a></li>
<li><a href="http://groups.google.com/group/django-lfs" target="_blank">Google Group</a></li>
<li><a href="http://twitter.com/lfsproject" target="_blank">lfsproject на Twitter</a></li>
<li><a href="irc://irc.freenode.net/django-lfs" target="_blank">IRC</a></li>
</ul>
"""


class Command(BaseCommand):
    args = ''
    help = 'Initializes LFS'

    def handle(self, *args, **options):
        from lfs.core.models import ActionGroup
        from lfs.core.models import Action
        from lfs.core.models import Application
        from lfs.core.models import Country
        from lfs.core.models import Shop
        from lfs.core.utils import import_symbol

        from portlets.models import Slot
        from portlets.models import PortletAssignment

        from lfs.portlet.models import CartPortlet
        from lfs.portlet.models import CategoriesPortlet
        from lfs.portlet.models import PagesPortlet
        from lfs.payment.models import PaymentMethod
        from lfs.payment.settings import PM_BANK
        from lfs.page.models import Page
        from lfs.shipping.models import ShippingMethod
        from lfs_additional_categories.models import AdditionalFilterPortlet
        from lfs.catalog.models import Category

        #Clear
        Country.objects.all().delete()
        Shop.objects.all().delete()
        ActionGroup.objects.all().delete()
        Action.objects.all().delete()
        Category.objects.all().delete()
        CartPortlet.objects.all().delete()
        CategoriesPortlet.objects.all().delete()
        PagesPortlet.objects.all().delete()
        AdditionalFilterPortlet.objects.all().delete()
        PortletAssignment.objects.all().delete()
        PaymentMethod.objects.all().delete()
        ShippingMethod.objects.all().delete()
        Page.objects.all().delete()
        Application.objects.all().delete()



        # Country
        russia = Country.objects.create(code="ru", name=u"Россия")

        # Shop
        shop = Shop.objects.create(name="LFS", shop_owner="John Doe",
            from_email="john@doe.com", notification_emails="john@doe.com", description=SHOP_DESCRIPTION, default_country=russia)
        shop.invoice_countries.add(russia)
        shop.shipping_countries.add(russia)

        # Actions
        tabs = ActionGroup.objects.create(name="Tabs")
        footer = ActionGroup.objects.create(name="Footer")
        Action.objects.create(group=tabs, title=u"Контакты", link="/contact", active=True, position=1)
        Action.objects.create(group=footer, title=u"Соглашение об использовании", link="/page/terms-and-conditions", active=True, position=1)
        Action.objects.create(group=footer, title="Imprint", link="/page/imprint", active=True, position=2)

        #Catalog
        category = Category.objects.create(name=u"Товары",
                                           slug="all",
                                           level=1,
                                           template=1)

        # Portlets
        left_slot = Slot.objects.create(name="Left")
        right_slot = Slot.objects.create(name="Right")
        centre_slot = Slot.objects.create(name="Centre")

        cart_portlet = CartPortlet.objects.create(title=u"Корзина")
        PortletAssignment.objects.create(slot=right_slot, content=shop, portlet=cart_portlet)

        categories_portlet = CategoriesPortlet.objects.create(title=u"Товары")
        PortletAssignment.objects.create(slot=left_slot, content=shop, portlet=categories_portlet)

        pages_portlet = PagesPortlet.objects.create(title=u"Информация")
        PortletAssignment.objects.create(slot=left_slot, content=shop, portlet=pages_portlet)

        additional_filter_portlet = AdditionalFilterPortlet.objects.create(title=u"Товары по модели",
                                                                           default_category=category)
        PortletAssignment.objects.create(slot=centre_slot, content=shop, portlet=additional_filter_portlet)

        # Payment methods
        pm = PaymentMethod.objects.create(name=u"Банковская карта", priority=1, active=1, deletable=0, type=PM_BANK)
        pm.id=1; pm.save()
        pm = PaymentMethod.objects.create(name=u"Оплата наличными при получении товара", priority=2, active=1, deletable=0)
        pm.id=2; pm.save()
        #pm = PaymentMethod.objects.create(name=u"PayPal", priority=3, active=1, deletable=0)
        #pm.id=3; pm.save()
        pm = PaymentMethod.objects.create(name=u"Предоплата", priority=4, active=1, deletable=0)
        pm.id=3; pm.save()

        # Shipping methods
        ShippingMethod.objects.create(name=u"Обычная доставка", priority=1, active=1)

        # Pages
        p = Page.objects.create(title=u"Главная страница", slug="", active=1, exclude_from_navigation=1)
        p.id = 1; p.save()
        p = Page.objects.create(title=u"Соглашение об использовании", slug="terms-and-conditions", active=1,
                                body=u"Введите текст соглашения об использовании.")
        p.id = 2; p.save()
        p = Page.objects.create(title="Imprint", slug="imprint", active=1, body="Enter your imprint here.")
        p.id = 3; p.save()

        # Order Numbers
        ong = import_symbol(settings.LFS_ORDER_NUMBER_GENERATOR)
        ong.objects.all().delete()
        ong.objects.create(id="order_number")

        # Application object
        Application.objects.create(version="0.7")
