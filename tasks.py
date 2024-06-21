import datetime
import time
from celery import Celery
from main_data import schedule_db_refresh
from celery.schedules import crontab
from service.mail_send import send_email
from constants import TIMEZONE
from m_logger_settings import logger
from database.schedule_calculation import weekends_get
from service.python_to_1C import python_to_1C

# celery_app = Celery('tasks', broker='localhost://redis:6370')
celery_app = Celery('tasks', broker='redis://redis:5370')
# celery_app = Celery('tasks', broker='172.25.0.2://redis:5370')


@celery_app.task()
def yesterday_from_db():
    end_date = (datetime.date.today() + datetime.timedelta(days=10)).strftime("%Y-%d-%m")
    start_date = (datetime.date.today() - datetime.timedelta(days=31)).strftime("%Y-%d-%m")
    # start_date = datetime.date.today() - datetime.timedelta(days=2)
    # end_date = datetime.date.today() + datetime.timedelta(days=2)
    schedule_db_refresh(start_date, end_date)


@celery_app.task()
def send_notification_mail():
    send_email('demad@mail.ru', 'celery выполнил задачу')

    send_email('ekimenko.m@gmail.com', 'celery выполнил задачу')
    logger.debug(f'CELERY выполнил задачу send_notification_mail {datetime.datetime.now()}')


@celery_app.task()
def weekends_filling() -> None:
    current_year = datetime.datetime.now().year
    weekends_get(current_year)


@celery_app.task()
def json_to_1C() -> None:
    end_date = (datetime.datetime.now() + datetime.timedelta(days=10)).strftime('%Y-%d-%m')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%d-%m')
    python_to_1C(start_date=start_date, end_date=end_date)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # время запуска выгрузки БД
    # db_upload_time = convert_time_to_utc('02:00')
    # время отправки письма
    # mail_send_time = convert_time_to_utc('19:10')
    # db_upload_time = '02:00'
    # utc_delta = int(time.localtime().tm_hour - time.gmtime().tm_hour)
    # chosen_date = datetime.datetime.strptime(f"{db_upload_time}+0{utc_delta}00", "%H:%M%z")
    # utc_db_upload_time = chosen_date - datetime.timedelta(hours=utc_delta)

    celery_app.conf.beat_schedule = {
        # выгрузка из БД
        'data_upload': {
            'task': 'tasks.yesterday_from_db',
            'schedule': crontab(hour=0, minute=5),
        },
        'json_1C': {
            'task': 'tasks.json_to_1C',
            'schedule': crontab(hour=0, minute=10),
        },
        # отправка письма
        'email_send': {
            'task': 'tasks.send_notification_mail',
            'schedule': crontab(hour=0, minute=10),
        },
        'latecomers': {
            'task': 'tasks.yesterday_from_db',
            'schedule': crontab(hour=2, minute=1),
        },
        'data_upload2': {
            'task': 'tasks.yesterday_from_db',
            'schedule': crontab(hour=23 - TIMEZONE, minute=45),
        },
        'json_1C2': {
            'task': 'tasks.json_to_1C',
            'schedule': crontab(hour=23 - TIMEZONE, minute=55),
        },
        # 'calendar_filling': {
        #     'task': 'tasks.weekends_filling',
        #     'schedule': crontab(month=6, day=13, year='*', hour=1),
        #
        # },
        # 'data_upload3': {
        #     'task': 'tasks.yesterday_from_db',
        #     'schedule': crontab(hour=1, minute=35),
        # },
        # 'json_1C3': {
        #     'task': 'tasks.json_to_1C',
        #     'schedule': crontab(hour=1, minute=45),
        # },
    }


if __name__ == '__main__':
    json_to_1C()
