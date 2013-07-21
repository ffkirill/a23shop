# django imports
from django.conf.urls.defaults import *

urlpatterns = patterns('lfs_additional_categories.views',
    #Hook for filtering
    url(r'^category-(?P<slug>[-\w]*)$', "lfs_category_hook", name="lfs_category"),
    #
    url(r'^reset-additional-filter/(?P<category_slug>[-\w]+)', "reset_filter", name="lfs_reset_additional_filter"),
    url(r'^set-additional-filter/(?P<category_slug>[-\w]+)/(?P<additional_category_id>\d*)', "set_filter",
        name="lfs_set_additional_filter"),
)