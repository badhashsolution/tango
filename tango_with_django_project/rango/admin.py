# WGG batteries-included, admin interface
from django.contrib import admin

#WGG  category and page models
from rango.models import Category, Page, UserProfile

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

# WGG Register models with the admin interface
admin.site.register(Category)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)


