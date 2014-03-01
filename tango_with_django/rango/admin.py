from django.contrib import admin
from rango.models import Category, Page, PageAdmin
from rango.models import UserProfile

admin.site.register(Category)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)