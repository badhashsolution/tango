from django.contrib import admin
from rango.models import Category, Page

# WGG Register models with the admin interface
admin.site.register(Category)
admin.site.register(Page)

