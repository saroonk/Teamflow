from celery import shared_task
from django.core.mail import send_mail

from django.conf import settings
from .models import Task
@shared_task
def send_task_assignment_email(task_id):
    try:
        task = Task.objects.get(id=task_id)
        subject = f"New Task Assigned: {task.title}"
        message = f"You have been assigned a new task:\n\nTitle: {task.title}\nDescription: {task.description}\nDue Date: {task.due_date}\n\nPlease check your dashboard for more details."
        recipient_list = [task.assigned_to.email]
        print(f"Sending email to: {recipient_list} with subject: {subject}")
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    except Task.DoesNotExist:
        print(f"Task with id {task_id} does not exist.")
        pass

