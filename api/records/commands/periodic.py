# records/management/commands/setup_periodic_tasks.py
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule


class Command(BaseCommand):
    help = "Setup periodic tasks for Celery"

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="8",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )
        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name="Send borrowing reminders daily",
            task="records.tasks.send_borrowing_reminders",
        )
        self.stdout.write(self.style.SUCCESS("Periodic tasks set up successfully."))
