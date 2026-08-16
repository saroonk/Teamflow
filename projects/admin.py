from django.contrib import admin

# Register your models here.


from unfold.admin import ModelAdmin
from .models import *

@admin.register(Project)
class CustomProject(ModelAdmin):
    list_display = ['id','title' , 'organization' ,'project_manager','priority','status']