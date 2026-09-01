from django.core.cache import cache


def invalidate_task_comments_cache(task_id):
    cache.delete_pattern(
        f"teamflow:user:*:task:{task_id}:comments:list:*"
    )