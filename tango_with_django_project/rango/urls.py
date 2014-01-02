# WGG this file contains urls specific to the rango project
from django.conf.urls import patterns, url
from rango import views

# WGG this tuple must be called urlpatterns for django to
# pick it up. ^$ matches an empty string, in this example
# http://www.tangowithdjango.com/rango/ is considered blank
urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'^category/(?P<category_name_url>\w+)/$', views.category, name='category'),
)

