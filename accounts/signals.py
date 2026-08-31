from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from projects.cache import invalidate_project_members_cache


@receiver(post_save, sender=User)
def invalidate_project_members_cache_on_user_update(sender,instance,created,**kwargs):
    if created:
        return

    for project in instance.projects.all():
        invalidate_project_members_cache(project.id)