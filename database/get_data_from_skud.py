import datetime
import os
import time
from pathlib import Path
from typing import Dict, Tuple
import pyodbc
from dotenv import load_dotenv
from settings import dotenv_path

try:
    from database.models_alchemy import Employee, Timesheet
    from database.database import session_factory
except ModuleNotFoundError:
    from models_alchemy import Employee, Timesheet
    from database import session_factory

from m_logger_settings import logger
from sqlalchemy import select, insert, update
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# данные для подключения к БД
BD_SERVER = os.getenv("SKUD_DB_HOST")
BD_DATABASE = os.getenv("SKUD_DB_NAME")
BD_USERNAME = os.getenv("SKUD_DB_USER")
BD_PASSWORD = os.getenv("SKUD_DB_PASSWORD")


POINTS = {
    'Турникет': (40, 41),
}

ONE_DAY = datetime.timedelta(days=1)
YESTERDAY = datetime.datetime.date(datetime.datetime.now() - ONE_DAY)






def get_skud_data(date_start=YESTERDAY, date_end=YESTERDAY, point=POINTS["Турникет"]):
    """
    Функция получения данных из СКУД
    :param date_start: дата начала
    :param date_end: дата окончания
    :param point: точка доступа СКУД
    :return:
    """
    with session_factory() as session:
        employees = {employee.fio: {"fio": employee}
                     for employee in session.execute(select(Employee)).scalars().all()}
    # интервал выгрузки
    date = date_start
    while date <= date_end:
        logger.info(f"Получение табеля за {date}.")
        # Получение данных СКУД
        timesheets = get_timesheets(employees=employees, date=date, point=point)
        created = updated = 0
        for employee, data in timesheets.items():
            try:
                with session_factory() as session:
                    # Существующая запись по fio_id
                    fio_id = select(Timesheet).where(Timesheet.employee_id == data["fio"].id,
                                                     Timesheet.date == date)
                    # данные для вставки
                    inserting_data = {key: val for key, val in data.items() if key != data['fio']}
                    inserting_data.update({'employee_id': data["fio"].id})
                    # если нет записи добавляем
                    if not session.execute(select(fio_id.exists())).scalars().first():
                        session.execute(insert(Timesheet), inserting_data)
                        session.commit()
                        created += 1
                    else:  # обновляем
                        session.execute(update(Timesheet).where(Timesheet.employee_id == data["fio"].id),
                                        inserting_data)
                        updated += 1
            except Exception as e:
                logger.exception(e)
                logger.error(f"Ошибка создании/обновлении записи в БД табелей с данными: {data}")
        logger.info(f"Успешно занесено в базу данных. {date} Обновлено: {updated}, создано: {created}")
        date += ONE_DAY


def get_night_shift_query(date, point, employees):
    """
    Функция формирования запроса в СКУД ночных смен.
    :param date: Дата
    :param point: точка доступа СКУД
    :param employees: словарь работников
    :return:
    """
    # ночное время
    night = (
        f"{date.strftime('%d.%m.%Y')} 12:00",
        f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 12:00"
    )
    # начало следующего дня
    next_day = f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 00:00"
    # окончание ночной смены
    end_night_shift = f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 04:00"
    start, end = night
    # состав ряда выгрузки запроса
    # (время работы, ФИО, id_skud, самое ранее время входа, самое позднее время выхода, сообщение, смена)
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
    """
    Функция формирования запроса в СКУД дневных смен.
    :param date: Дата
    :param point: точка доступа СКУД
    :param employees: словарь работников
    :return:
    """
    # продолжительность дневной смены
    day = (
        f"{date.strftime('%d.%m.%Y')} 06:00",
        f"{(date + ONE_DAY).strftime('%d.%m.%Y')}"
    )
    start, end = day
    # состав ряда выгрузки запроса
    # (время работы, ФИО, id_skud, самое ранее время входа, самое позднее время выхода, сообщение, смена)
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
    """
    Получение детальной ошибки при выполнении запроса
    :param date:
    :param employee_id:
    :return:
    """
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


def get_timesheets(employees: Dict, date: datetime, point: Tuple):
    """
    Получение времени работы из СКУД
    :param employees:
    :param date:
    :param point:
    :return:
    """
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
            get_day_shift_query(date, point, employees),
            get_night_shift_query(date, point, employees)
        ]
        # Обновляем словарь с сотрудниками данными из БД СКУД
        for query in queries:
            errors = execute_query(query=query, action=query_row_handler, result=employees, errors=errors)
    return employees


def query_row_handler(row, result, errors):
    """
    Обработка каждого ряда выгрузки из СКУД
    :param row:
    :param result:
    :param errors:
    :return:
    """
    duration, employee, employee_id, enter_time, exit_time, msg, shift = row
    employee = " ".join(employee.split())  # убираем лишние пробелы по краям и между ФИО

    try:
        date = result[employee]['date']
        if duration and duration < 0:
            duration = None
        if errors and employee in errors and msg != "Ошибка":
            result[employee].update({
                'skud_error': False,
                'skud_error_query': None,
            })
            logger.info(f"Обновлено: {row}")

        if msg == 'Ошибка':
            # получаем табель сотрудника за прошлый день,
            # если время выхода совпадают, значит работал в ночь и это не ошибка
            with (session_factory() as session):
                prev_timesheet = session.execute(select(Timesheet).where(
                    Timesheet.employee_id == result[employee]['fio'].id, Timesheet.date == date - ONE_DAY)
                ).scalars().all()
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
                result[employee].update({
                    'skud_error': True,
                    'skud_error_query': get_detail_error_query(date=date, employee_id=employee_id)
                })
                logger.warning(f"Ошибка отметки: {error_msg} {row}")

        if shift == 'Дневная':
            result[employee].update({
                'skud_day_start_1': enter_time,
                'skud_day_end_1': exit_time,
                'skud_day_duration': duration,
            })

        elif shift == 'Ночная':
            end_current_date = (datetime.datetime.combine(
                date=date,
                time=datetime.time(23, 59, 59)
            ))

            next_day = (datetime.datetime.combine(
                date=date + ONE_DAY,
                time=datetime.time(00, 00, 00)
            ))

            end_day_shift = (datetime.datetime.combine(
                date=date,
                time=datetime.time(22, 00, 00)
            ))

            end_night_shift = (datetime.datetime.combine(
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
                logger.warning(f'Неучтенный период работы с {enter_time} до {exit_time}')
        else:
            logger.warning(f'Неизвестный статус смены: {shift}')
    except KeyError as e:
        logger.error(f'Несовпадение ключей: {employee}. ')
        logger.exception(e)
    return errors


def execute_query(query, result=None, errors=None, action=None):
    """
    Функция запускает запросы в БД
    :param query:
    :param result:
    :param errors:
    :param action:
    :return:
    """
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
    except Exception as e:
        logger.error(f'Ошибка выполнения запроса {query}')
        logger.exception(e)
    finally:
        cnxn.close()


def count_hours(start, end):
    return int((end - start).total_seconds() / 3600)


if __name__ == '__main__':
    # ручная выгрузка интервала
    # date_string = '2024-04-10'
    # random_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
    # today = datetime.datetime.now().date()
    # get_skud_data(date_start=random_date, date_end=today)
    # вчерашняя выгрузка
    get_skud_data()


