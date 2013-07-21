# django imports
from django.db.models.signals import post_syncdb

# lfs imports
from models import AdditionalFilterPortlet

# 3rd party imports
import portlets
from portlets.utils import register_portlet


def register_portlets(sender, **kwargs):
    # don't register our portlets until the table has been created by syncdb
    if sender == portlets.models:
        register_portlet(AdditionalFilterPortlet, "Addinional category filter")

post_syncdb.connect(register_portlets)
