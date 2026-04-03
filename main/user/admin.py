from django.contrib import admin

from .forms import User


@admin.register(User)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['username','first_name', 'last_name', 'email']
    search_fields = ['username',]

