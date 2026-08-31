from django.core.cache import cache


def invalidate_project_members_cache(project_id):
    cache.delete(f"teamflow:project:{project_id}:members:list")