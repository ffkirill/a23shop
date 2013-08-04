# django imports
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'custom_backup.views',
    url(r'^dump', "process", name="backup"),

)
