import datetime
import time
from celery import Celery
from main_data import schedule_db_refresh
from celery.schedules import crontab
from service.mail_send import send_email

# celery_app = Celery('tasks', broker='localhost://redis:6370')
celery_app = Celery('tasks', broker='redis://redis:5370')


@celery_app.task()
def yesterday_from_db(start_date: str = None, end_date: str = None):
    schedule_db_refresh()


@celery_app.task()
def send_notification_mail():
    send_email('demad@mail.ru', 'celery выполнил задачу')

    send_email('ekimenko.m@gmail.com', 'celery выполнил задачу')


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # TODO перенести в services
    def convert_time_to_utc(time_str: str) -> datetime:
        utc_delta = int(time.localtime().tm_hour - time.gmtime().tm_hour)
        chosen_date = datetime.datetime.strptime(f"{time_str}+0{utc_delta}00", "%H:%M%z")
        return chosen_date - datetime.timedelta(hours=utc_delta)


    # время запуска выгрузки БД
    db_upload_time = convert_time_to_utc('02:00')
    # время отправки письма
    mail_send_time = convert_time_to_utc('19:10')
    # db_upload_time = '02:00'
    # utc_delta = int(time.localtime().tm_hour - time.gmtime().tm_hour)
    # chosen_date = datetime.datetime.strptime(f"{db_upload_time}+0{utc_delta}00", "%H:%M%z")
    # utc_db_upload_time = chosen_date - datetime.timedelta(hours=utc_delta)

    celery_app.conf.beat_schedule = {
        # выгрузка из БД
        'data_upload': {
            'task': 'tasks.yesterday_from_db',
            'schedule': crontab(hour=db_upload_time.hour, minute=db_upload_time.minute),
        },
        # отправка письма
        'email_send': {
            'task': 'tasks.send_notification_mail',
            'schedule': crontab(hour=mail_send_time.hour, minute=mail_send_time.minute),
        },
        # тестовая отправка
        'email_send2': {
            'task': 'tasks.send_notification_mail',
            'schedule': crontab(hour=mail_send_time.hour, minute=mail_send_time.minute),
        },
        'email_send3': {
            'task': 'tasks.send_notification_mail',
            'schedule': crontab(hour=db_upload_time.hour, minute=db_upload_time.minute),
        }
    }

