from django.contrib import admin

# Register your models here.


from .models import Comment
from unfold.admin import ModelAdmin

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['id','content', 'created_by', 'task', 'created_at']