from django.conf.urls import include, url

urlpatterns = [
    url(r'^(\w+)/(\d+)/(\d+)/(\d+)/booking/(\d+)/$', 'rtut.views.booking'),
    url(r'^(\w+)/(\d+)/(\d+)/(\d+)/$', 'rtut.views.day'),
    url(r'^def/$', 'rtut.views.defcal'),
    url(r'^(\w+)$', 'rtut.views.cal'),
    url(r'^$', 'rtut.views.all'),
]
