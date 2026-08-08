from django.db import models

# Create your models here.




class Organizations(models.Model):
    name = models.CharField(max_length=150 , unique=True , db_index=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)