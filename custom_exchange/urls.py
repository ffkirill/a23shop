# django imports
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('custom_exchange.views',
    url(r'^1cbitrix', "process", name="exchange"),

)
