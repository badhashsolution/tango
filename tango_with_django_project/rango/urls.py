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
    # WGG added this for pages not sure i need it
    # url(r'^pages/(?P<page__name_url>\w+)/$', views.category, name='category'),
    url(r'^add_category/$', views.add_category, name='add_category'),
    url(r'^category/(?P<category_name_url>\w+)/add_page/$', views.add_page, name='add_page'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name="login"),
    url(r'^restricted/', views.restricted, name='restricted'),
    url(r'^logout/$', views.user_logout, name='logout'),
)

