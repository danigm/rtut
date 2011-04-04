from django.conf.urls.defaults import *


urlpatterns = patterns('rtut.views',
    (r'^(\w+)/(\d+)/(\d+)/(\d+)/booking/(\d+)/$', 'booking'),
    (r'^(\w+)/(\d+)/(\d+)/(\d+)/$', 'day'),
    (r'^def/$', 'defcal'),
    (r'^(\w+)$', 'cal'),
    (r'^$', 'all'),
)
