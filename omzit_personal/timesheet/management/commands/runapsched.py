import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from timesheet.management.commands.getskuddata import get_skud_data

logger = logging.getLogger("logger")


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=1*7*24*60*60):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            get_skud_data,
            trigger=CronTrigger(day="*/1", hour="00"),  # Каждый день в 00:00
            id="Получение данных со СКУД за день",
            misfire_grace_time=60,  # отсрочка 60 сек
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача ежедневного получения данных со СКУД")

        logger.info("Запуск планировщика...")
        scheduler.start()
