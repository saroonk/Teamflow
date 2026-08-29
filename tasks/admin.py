from django.contrib import admin

# Register your models here.


from unfold.admin import ModelAdmin
from .models import *

@admin.register(Task)
class CustomTask(ModelAdmin):
    list_display = ['id','title' , 'project' ,'assigned_to','priority','status']