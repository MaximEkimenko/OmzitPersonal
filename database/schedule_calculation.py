import pandas as pd
from pandas import DatetimeIndex
from sqlalchemy import select, update
import datetime
import os
import requests
from dotenv import load_dotenv
from constants import dotenv_path
from constants import MODE

# if MODE == 'test':
#     from constants import test_dotenv_path as dotenv_path
# if MODE == 'docker':
#     from constants import dotenv_path as dotenv_path
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)

from m_logger_settings import logger

try:
    from database.models import Employee, Timesheet, CalendarDays
    from database.database import session_factory, async_session_factory
except Exception:
    from models import Employee, Timesheet, CalendarDays
    from database import session_factory, engine


def weekends_get(year: int) -> tuple:
    """
    Заполняет таблицу calendar_days данными с API сайта https://isdayoff.ru/extapi
    :param year: год
    :return: tuple выходные, рабочие, сокращённые
    """
    url = f'https://isdayoff.ru/api/getdata?year={year}&pre=1'
    start_of_year = datetime.datetime(int(year), 1, 1)  # первый день года
    r = requests.get(url)
    days = r.text
    weekends = []
    workdays = []
    shortdays = []
    with session_factory() as session:
        for nday, day in enumerate(days):
            date = start_of_year + datetime.timedelta(days=nday)
            exist_calendar = session.execute(select(CalendarDays).where(CalendarDays.date == date)).scalar()
            if not exist_calendar:
                if day == '0':
                    day_type = 'Рабочий'
                    workdays.append(date.strftime('%d.%m.%Y'))
                if day == '1':
                    day_type = 'Выходной'
                    weekends.append(date.strftime('%d.%m.%Y'))
                if day == '2':
                    day_type = 'Сокращённый'
                    shortdays.append(date.strftime('%d.%m.%Y'))
                new_record = CalendarDays(date=date, day_type=day_type)
                session.add(new_record)

            else:
                logger.info(f'Данные на {date} - {exist_calendar.day_type} уже есть в БД')
        session.commit()
        logger.info(f'{year} добавлено в calendar_days')
    return weekends, workdays, shortdays


def insert_weekend_5_2(fio_id: int, dates: DatetimeIndex) -> None:
    """
    Заполняет выходные дни для фио в списке dates
    :return: None
    """
    for date in dates:
        with (session_factory() as session):
            # Проверка если день рабочий
            base_day = session.execute(select(CalendarDays).where(CalendarDays.date == date)).scalar()
            # print(base_day.day_type)
            if base_day.day_type != 'Рабочий' and base_day.day_type != 'Сокращённый':
                # Существующая запись
                query = (
                    select(Timesheet, CalendarDays)
                    .join(Employee, Employee.id == Timesheet.employee_id)
                    .join(CalendarDays, CalendarDays.date == Timesheet.date)
                    .where(Employee.id == fio_id)
                    .where(Timesheet.date == date)
                )
                if session.execute(query).all():
                    # проверяем статус дня
                    timesheet, days = session.execute(query).first()
                    if days.day_type == "Выходной":
                        # обновляем запись
                        session.execute(update(Timesheet).values(day_status='Выходной', day_status_short='В',
                                                                 skud_day_duration=0)
                                        .where(Timesheet.employee_id == fio_id, Timesheet.date == date))
                else:
                    # добавляем новую запись
                    new_record = Timesheet(date=date, employee_id=fio_id, day_status_short='В',
                                           day_status='Выходной',  skud_day_duration=0)
                    session.add(new_record)
                    logger.debug(f'Для {fio_id} {date} добавлена новая запись {new_record}')
            session.commit()


# 5/2
def schedule_5_2(fio_id: int = None) -> None:
    """
    Заполняет выходные для fio при выборе графика 5/2 на весь год
    :return: None
    """
    # получение всех / или fio_id фио с графиком 5/2
    with (session_factory() as session):
        if fio_id:
            query = (select(Employee).where(Employee.schedule == '5/2',  Employee.id == fio_id))
        else:
            query = (select(Employee).where(Employee.schedule == '5/2'))
        fios = session.execute(query).scalars().all()
    # получение интервала дат
    today = datetime.datetime.today().date()
    end_of_year = datetime.datetime(today.year, 12, 31).date()  # конец года
    dates = pd.date_range(start=today, end=end_of_year)
    # Обновление / добавление существующих выходных
    for fio in fios:
        insert_weekend_5_2(fio.id, dates)
        logger.info(f"Для {fio.id} {fio.fio} были обновлены выходные дни")


if __name__ == '__main__':
    tst_date = [datetime.datetime.strptime('2024-06-06', '%Y-%m-%d'),
                datetime.datetime.strptime('2024-06-07', '%Y-%m-%d'),
                datetime.datetime.strptime('2024-06-10', '%Y-%m-%d'),
                datetime.datetime.strptime('2024-06-11', '%Y-%m-%d'),
                datetime.datetime.strptime('2024-06-12', '%Y-%m-%d'),
                ]
    # insert_weekend_5_2(637, tst_date)

    tst_year = 2024
    # schedule_5_2()
    print(weekends_get(tst_year)[0])
