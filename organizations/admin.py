
from django.contrib import admin

from unfold.admin import ModelAdmin
from .models import Organizations

@admin.register(Organizations)
class Customorganisations(ModelAdmin):
    list_display = ['name' , 'created_at']
