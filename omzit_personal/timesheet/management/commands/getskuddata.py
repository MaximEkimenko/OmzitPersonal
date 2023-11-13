import datetime
import logging
import os
import time

from typing import Dict

import pyodbc
from django.core.management import BaseCommand
from django.utils.timezone import make_aware

from timesheet.models import Employee, Timesheet

logger = logging.getLogger("logger")

POINTS = {
    'Турникет': (40, 41),
}

ONE_DAY = datetime.timedelta(days=1)
YESTERDAY = datetime.datetime.date(datetime.datetime.now() - ONE_DAY)

# данные для подключения к БД
BD_SERVER = os.getenv("SKUD_DB_HOST")
BD_DATABASE = os.getenv("SKUD_DB_NAME")
BD_USERNAME = os.getenv("SKUD_DB_USER")
BD_PASSWORD = os.getenv("SKUD_DB_PASSWORD")


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        employees = {employee.fio: {"fio": employee} for employee in Employee.objects.all()}
        # интервал выгрузки
        date = datetime.date(day=1, month=5, year=2023)
        date_end = datetime.date(day=30, month=11, year=2023)
        # date = date_end = YESTERDAY
        while date <= date_end:
            logger.info(f"Получение табеля за {date}...")
            timesheets = get_timesheets(employees=employees, date=date)
            created = updated = 0
            for employee, data in timesheets.items():
                try:
                    _, is_created = Timesheet.objects.update_or_create(
                        fio=data["fio"],
                        date=data["date"],
                        defaults=data,
                    )
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                except Exception as ex:
                    logger.error(f"Исключение {ex} при создании/обновлении записи в БД табелей с данными: {data}")
            logger.info(f"{date} Обновлено: {updated}, создано: {created}")
            date += ONE_DAY


def get_night_shift_query(date, point, employees):
    night = (
        f"{date.strftime('%d.%m.%Y')} 12:00",
        f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 12:00"
    )
    next_day = f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 00:00"
    end_night_shift = f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 04:00"

    start, end = night
    query = f"""
        SELECT 
            ROUND((DATEDIFF(minute, MAX(t1.enter_time), MAX(t1.exit_time)))/60, 0, 1) as work_time, 
            t1.FIO, 
            t1.HozOrgan, 
            MAX(t1.enter_time), 
            MAX(t1.exit_time),
            CASE
                WHEN MAX(t1.enter_time) >= MAX(t1.exit_time) OR MAX(t1.enter_time) is Null OR MAX(t1.exit_time) is Null
                    THEN 'Ошибка'
                ELSE 'ОК'
            END AS Correct,
            'Ночная'
        FROM
            (SELECT
                t2.HozOrgan,
                pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName AS FIO,
                t2.Mode,
                CASE 
                    WHEN t2.Mode = 1
                        THEN t2.TimeVal
                    ELSE Null
                END AS enter_time,
                CASE 
                    WHEN t2.Mode = 2
                        THEN t2.TimeVal
                    ELSE Null
                END AS exit_time,
                t2.TimeVal
            FROM pLogData AS t2
            JOIN pList ON t2.HozOrgan = pList.ID
            WHERE (t2.TimeVal >= ?
            AND t2.TimeVal < ?
            AND pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName in {tuple(employees)}
            AND t2.Event in (13, 29, 32)
            AND t2.DoorIndex in {point})
            ) AS t1
        GROUP BY t1.FIO, t1.HozOrgan
        HAVING (DATEDIFF(day, MAX(t1.enter_time), MAX(t1.exit_time)) = 1) 
                OR (MAX(t1.enter_time) >= ? AND MAX(t1.enter_time) <= ?);
        """, start, end, next_day, end_night_shift
    return query


def get_day_shift_query(date, point, employees):
    day = (
        f"{date.strftime('%d.%m.%Y')} 06:00",
        f"{(date + ONE_DAY).strftime('%d.%m.%Y')}"
    )
    start, end = day
    query = f"""
        SELECT
            ROUND((DATEDIFF(minute, MIN(t1.enter_time), MAX(t1.exit_time)) - 60)/60, 0, 1) as work_time,
            t1.FIO,
            t1.HozOrgan,
            MIN(t1.enter_time),
            MAX(t1.exit_time),
            CASE
                WHEN MIN(t1.enter_time) >= MAX(t1.exit_time) OR MIN(t1.enter_time) is Null OR MAX(t1.exit_time) is Null
                    THEN 'Ошибка'
                ELSE 'ОК'
            END AS Correct,
            'Дневная'
        FROM
            (SELECT
                t2.HozOrgan,
                pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName AS FIO,
                t2.Mode,
                CASE
                WHEN t2.Mode = 1
                THEN t2.time
                ELSE Null
                END AS enter_time,
                CASE
                WHEN t2.Mode = 2
                THEN t2.time
                ELSE Null
                END AS exit_time,
                t2.time
            FROM
                (SELECT
                    CASE
                        WHEN DATEPART(hour, pLogData.TimeVal) < 8 AND pLogData.Mode = 1
                            THEN SMALLDATETIMEFROMPARTS (
                                    YEAR(pLogData.TimeVal), 
                                    MONTH(pLogData.TimeVal), 
                                    DAY(pLogData.TimeVal), 
                                    8, 00
                                    )
                        ELSE pLogData.TimeVal
                        END AS time, *
                 FROM pLogData
                ) AS t2
            JOIN pList ON t2.HozOrgan = pList.ID
            WHERE (t2.TimeVal >= ?
            AND t2.TimeVal < ?
            AND pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName in {tuple(employees)}
            AND t2.Event in (13, 29, 32)
            AND t2.DoorIndex in {point})
            ) AS t1
        GROUP BY t1.FIO, t1.HozOrgan, DATEPART(day, t1.time)
        HAVING MAX(t1.exit_time) >= SMALLDATETIMEFROMPARTS (
                                            YEAR(MAX(t1.exit_time)), 
                                            MONTH(MAX(t1.exit_time)), 
                                            DAY(MAX(t1.exit_time)), 
                                            8, 00)
                OR MAX(t1.exit_time) is Null;
        """, start, end
    return query


def get_detail_error_query(date, employee_id):
    day = (
        f"{(date - ONE_DAY).strftime('%d.%m.%Y')}",
        f"{(date + ONE_DAY + ONE_DAY).strftime('%d.%m.%Y')}"
    )
    start, end = day
    query = " ".join(f"""
      SELECT *
      FROM pLogData
      WHERE HozOrgan = {employee_id} AND TimeVal >= '{start}' AND TimeVal < '{end}'
      ORDER BY TimeVal
    """.split())
    return query


def get_timesheets(employees: Dict, date: datetime = YESTERDAY, point: str = 'Турникет'):
    # Добавляем всех выбранных сотрудников в словарь с нулевыми значениями
    for employee in employees:
        employees[employee].update({
            'date': date,
            'skud_day_start_1': None,
            'skud_day_end_1': None,
            'skud_day_duration': None,
            'skud_night_duration': None,
            "skud_error": False,
        })
    errors = []
    # для будущих записей к БД не обращаемся
    if date <= datetime.date.today():
        queries = [
            get_day_shift_query(date, POINTS[point], employees),
            get_night_shift_query(date, POINTS[point], employees)
        ]
        # Обновляем словарь с сотрудниками данными из БД СКУД
        for query in queries:
            errors = execute_query(query=query, action=query_row_handler, result=employees, errors=errors)
    return employees


def query_row_handler(row, result, errors):
    duration, employee, employee_id, enter_time, exit_time, msg, shift = row
    employee = " ".join(employee.split())  # убираем лишние пробелы по краям и между ФИО
    date = result[employee]['date']
    if duration and duration < 0:
        duration = None

    if enter_time:
        enter_time = make_aware(enter_time)
    if exit_time:
        exit_time = make_aware(exit_time)

    if errors and employee in errors:
        logger.info(f"Обновлено: {row}")
        if msg != "Ошибка":
            result[employee].update({
                'skud_error': False,
            })

    if msg == 'Ошибка':
        # получаем табель сотрудника за прошлый день,
        # если время выхода совпадают, значит работал в ночь и это не ошибка
        prev_timesheet = result[employee]['fio'].timesheet.filter(date=date - ONE_DAY)
        if prev_timesheet and prev_timesheet[0].skud_day_end_1 == exit_time:
            return errors
        else:
            errors.append(employee)
            if not enter_time:
                error_msg = "Ошибка входа:"
            elif not exit_time:
                error_msg = "Ошибка выхода:"
            else:
                error_msg = "Ошибка выход раньше входа:"
            logger.warning(f"{error_msg} {row}")
            result[employee].update({
                'skud_error': True,
                'skud_error_query': get_detail_error_query(date=date, employee_id=employee_id)
            })

    if shift == 'Дневная':
        result[employee].update({
            'skud_day_start_1': enter_time,
            'skud_day_end_1': exit_time,
            'skud_day_duration': duration,
        })

    elif shift == 'Ночная':

        end_current_date = make_aware(datetime.datetime.combine(
            date=date,
            time=datetime.time(23, 59, 59)
        ))

        next_day = make_aware(datetime.datetime.combine(
            date=date + ONE_DAY,
            time=datetime.time(00, 00, 00)
        ))

        end_day_shift = make_aware(datetime.datetime.combine(
            date=date,
            time=datetime.time(22, 00, 00)
        ))

        end_night_shift = make_aware(datetime.datetime.combine(
            date=date + ONE_DAY,
            time=datetime.time(6, 00, 00)
        ))

        # с 18 до 7
        if enter_time < end_day_shift and exit_time > end_night_shift:
            result[employee].update({
                'skud_day_duration': count_hours(start=enter_time, end=end_day_shift) + count_hours(
                    start=end_night_shift, end=exit_time),
                'skud_day_start_1': enter_time,
                'skud_day_end_1': exit_time,
                'skud_night_duration': count_hours(start=end_day_shift, end=end_night_shift) - 1,
            })

        # с 18 до 6
        elif enter_time < end_day_shift and exit_time <= end_night_shift:
            result[employee].update({
                'skud_day_duration': count_hours(start=enter_time, end=end_day_shift),
                'skud_day_start_1': enter_time,
                'skud_day_end_1': exit_time,
                'skud_night_duration': (count_hours(start=end_day_shift, end=exit_time) - 1) if count_hours(
                    start=end_day_shift, end=exit_time) > 0 else 0,
            })
        # с 22 до 7
        elif end_day_shift <= enter_time <= end_current_date and exit_time > end_night_shift:
            result[employee].update({
                'skud_day_duration': count_hours(start=end_night_shift, end=exit_time),
                'skud_day_start_1': enter_time,
                'skud_day_end_1': exit_time,
                'skud_night_duration': count_hours(start=enter_time, end=end_night_shift) - 1,
            })

        # с 22 до 6
        elif end_day_shift <= enter_time <= end_current_date and exit_time <= end_night_shift:
            result[employee].update({
                'skud_day_duration': 0,
                'skud_day_start_1': enter_time,
                'skud_day_end_1': exit_time,
                'skud_night_duration': count_hours(start=enter_time, end=exit_time) - 1,
            })
        # с 00 до 7
        elif enter_time >= next_day and exit_time > end_night_shift:
            result[employee].update({
                'skud_day_duration': count_hours(start=end_night_shift, end=exit_time),
                'skud_day_start_1': enter_time,
                'skud_day_end_1': exit_time,
                'skud_night_duration': count_hours(start=enter_time, end=end_night_shift) - 1,
            })
        # с 00 до 6
        elif enter_time >= next_day and exit_time <= end_night_shift:
            result[employee].update({
                'skud_day_duration': 0,
                'skud_day_start_1': enter_time,
                'skud_day_end_1': exit_time,
                'skud_night_duration': count_hours(start=enter_time, end=exit_time) - 1 if count_hours(
                    start=enter_time, end=exit_time) > 0 else 0,
            })
        else:
            logger.error(f'Неучтенный период работы с {enter_time} до {exit_time}')
    else:
        logger.error(f'Неизвестный статус смены: {shift}')
    return errors


def execute_query(query, action, result, errors):
    start = time.time()
    try:
        cnxn = pyodbc.connect(
            f'DRIVER=SQL Server;'
            f'SERVER={BD_SERVER};'
            f'DATABASE={BD_DATABASE};'
            f'UID={BD_USERNAME};'
            f'PWD={BD_PASSWORD}',
        )
        cursor = cnxn.cursor()
        cursor.execute(*query)
        row = cursor.fetchone()
        while row:
            errors = action(row, result, errors)
            row = cursor.fetchone()
        logger.info(f"Завершение запроса в БД СКУД. Время выполнения {time.time() - start}")
        return errors
    except Exception:
        logger.exception(f"Исключение при работе с БД СКУД")
    finally:
        cnxn.close()


def count_hours(start, end):
    return int((end - start).total_seconds() / 3600)
