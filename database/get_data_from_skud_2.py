from contextlib import contextmanager

from sqlalchemy import select, insert, update, event
import datetime
import os
import time
from copy import copy
from pathlib import Path
from typing import Dict, Tuple
import pyodbc
from dotenv import load_dotenv
from constants import dotenv_path
from constants import TIMEZONE

try:
    from database.models import Employee, Timesheet
    from database.database import session_factory, async_session_factory
except Exception:
    from models import Employee, Timesheet
    from database import session_factory, engine

from m_logger_settings import logger

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def query_create(query_type: str,
                 start_date: str = None,
                 end_date: str = None,
                 access_point: str = 'Турникет') -> str:
    """
    :param query_type: variants = 'enter', 'exit', 'late_800', 'late_830'
    :param start_date:
    :param end_date:
    :param access_point:
    :return:
    """
    if not start_date:
        start_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%d-%m")
    if not end_date:
        end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%d-%m")
    is_exit = 'Выход'
    is_enter = 'Вход'
    today = datetime.date.today().strftime("%Y-%d-%m")
    # время начала работы для опоздавших
    time_day_start_800 = f'{today} 08:01:00'
    time_day_start_830 = f'{today} 08:31:00'
    # значения по умолчанию

    condition_enter = ''
    condition_exit = ''
    condition_latecomers_800 = ''
    condition_latecomers_830 = ''
    # условие от вида запроса
    if query_type == 'enter':
        condition_enter = f"""WHERE (pLogData.TimeVal >= '{start_date}' AND pLogData.TimeVal <= '{end_date}')
                    AND dbo.pLogData.Remark like '%{access_point}%' 
                    AND dbo.pLogData.Remark like '%{is_enter}%'"""
        order_by = 'ASC'
    elif query_type == 'exit':
        condition_exit = f"""WHERE (pLogData.TimeVal >= '{start_date}' AND pLogData.TimeVal <= '{end_date}')
                            AND dbo.pLogData.Remark like '%{access_point}%' 
                            AND dbo.pLogData.Remark like '%{is_exit}%'"""
        order_by = 'DESC'
    elif query_type == 'late_800':
        condition_latecomers_800 = f"""WHERE (pLogData.TimeVal >= {time_day_start_800})
                    AND dbo.pLogData.Remark like '%{access_point}%' 
                    AND dbo.pLogData.Remark like '%{is_enter}%' """
        order_by = 'DESC'
    elif query_type == 'late_830':
        condition_latecomers_830 = f"""WHERE (pLogData.TimeVal >= {time_day_start_830})
                        AND dbo.pLogData.Remark like '%{access_point}%' 
                        AND dbo.pLogData.Remark like '%{is_enter}%'"""
        order_by = 'DESC'
    # основной запрос
    query = f"""
    WITH MaxTimeValPerDateCTE AS (
    SELECT 
        pList.ID, 
        pLogData.HozOrgan,
        pLogData.TimeVal AS datetime,
        pLogData.Remark AS detail,
        pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName AS FIO,
        PCompany.Name AS company, 
        PPost.Name AS post,
        ROW_NUMBER() OVER (PARTITION BY pList.ID, CAST(pLogData.TimeVal AS DATE) ORDER BY pLogData.TimeVal {order_by}) AS rn
    FROM dbo.pLogData
    JOIN dbo.pList ON pLogData.HozOrgan = pList.ID
    JOIN dbo.PCompany ON pList.Company = PCompany.ID
    JOIN dbo.PPost ON pList.Post = PPost.ID 
    {condition_enter}{condition_exit}{condition_latecomers_800}{condition_latecomers_830}
    )
    SELECT DISTINCT 
    ID, 
    HozOrgan,
    datetime,
    detail,
    FIO,
    company, 
    post
    FROM MaxTimeValPerDateCTE
    WHERE rn = 1
    ORDER BY datetime;
    """

    # query = f"""SELECT DISTINCT t.ID, t.HozOrgan, t.datetime, t.detail, t.FIO, t.company, t.post
    # FROM (SELECT pList.ID, pLogData.HozOrgan,
    #              pLogData.TimeVal AS datetime,
    #              pLogData.Remark AS detail,
    #              pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName AS FIO,
    #              PCompany.Name AS company, PPost.Name AS post,
    #              ROW_NUMBER() OVER (PARTITION BY pLogData.HozOrgan ORDER BY pLogData.TimeVal {order_by}) AS rn
    #         FROM dbo.pLogData
    #         JOIN dbo.pList ON pLogData.HozOrgan = pList.ID
    #         JOIN dbo.PCompany ON pList.Company = PCompany.id
    #         JOIN dbo.PPost ON pList.Post = PPost.ID
    #         {condition_enter}{condition_exit}{condition_latecomers_800}{condition_latecomers_830}
    #         ) t
    #         WHERE t.rn = 1
    #         """
    return query


# WITH MaxTimeValPerDateCTE AS (
#     SELECT
#         pList.ID,
#         pLogData.HozOrgan,
#         pLogData.TimeVal AS datetime,
#         pLogData.Remark AS detail,
#         pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName AS FIO,
#         PCompany.Name AS company,
#         PPost.Name AS post,
#         ROW_NUMBER() OVER (PARTITION BY pList.ID, CAST(pLogData.TimeVal AS DATE) ORDER BY pLogData.TimeVal DESC) AS rn
#     FROM dbo.pLogData
#     JOIN dbo.pList ON pLogData.HozOrgan = pList.ID
#     JOIN dbo.PCompany ON pList.Company = PCompany.ID
#     JOIN dbo.PPost ON pList.Post = PPost.ID
#     WHERE (pLogData.TimeVal >= '2024-20-05' AND pLogData.TimeVal <= '2024-23-05')
#         AND pLogData.Remark LIKE '%Турникет%'
#         AND pLogData.Remark LIKE '%Вход%'
# )
# SELECT DISTINCT
#     ID,
#     HozOrgan,
#     datetime,
#     detail,
#     FIO,
#     company,
#     post
# FROM MaxTimeValPerDateCTE
# WHERE rn = 1
# ORDER BY datetime;


def query_execute(query: str, driver: str = 'DRIVER=SQL Server;'):
    """
    Выполнение запроса query
    :param query: текст запроса
    :param driver: sql driver для
    docker: f'DRIVER=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1;'
    :return:
    """
    BD_SERVER = os.getenv("SKUD_DB_HOST")
    BD_DATABASE = os.getenv("SKUD_DB_NAME")
    BD_USERNAME = os.getenv("SKUD_DB_USER")
    BD_PASSWORD = os.getenv("SKUD_DB_PASSWORD")
    result = []
    start = time.time()
    try:
        cnxn = pyodbc.connect(
            # f'DRIVER=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1;'  # для docker
            # f'DRIVER=ODBC Driver 17 for SQL Server;'
            f'{driver}'
            f'SERVER={BD_SERVER};'
            f'DATABASE={BD_DATABASE};'
            f'UID={BD_USERNAME};'
            f'PWD={BD_PASSWORD}',
        )
        cursor = cnxn.cursor()
        row = cursor.execute(query).fetchall()
        result = tuple(row)
        logger.info(f"Завершение запроса в БД СКУД. Время выполнения {time.time() - start}")
    except Exception as e:
        logger.error(f'Ошибка выполнения запроса {query}')
        logger.exception(e)
    finally:
        cnxn.close()
    return result


def get_tabel_skud(start_date: str = None, end_date: str = None):
    """
    Получение данных СКУД в интервале start_date end_date
    :param start_date:
    :param end_date:
    :return:
    """
    # получение данных
    enters = query_execute(query_create('enter', start_date, end_date))
    # print(enters)
    outs = query_execute(query_create('exit', start_date, end_date))
    nighties = []  # список возможных ночников
    results_line = dict()  # словарь строки результата
    results = []  # список результатов
    # определение длительности работы
    for enter in enters:
        for out in outs:
            if enter[4] == out[4] and enter[2].day == out[2].day:
                fio = enter[4]
                fio_enter = enter[2]  # вход для fio
                fio_out = out[2]  # выход для fio
                date = datetime.datetime(year=fio_enter.year, month=fio_enter.month, day=fio_enter.day,
                                         hour=0, minute=1)
                # обработка входа раньше если вход раньше 8:00, то вход = 8:00
                if fio_enter < datetime.datetime(year=fio_enter.year, month=fio_enter.month,
                                                 day=fio_enter.day, hour=8, minute=0):
                    fio_enter = datetime.datetime(year=fio_enter.year, month=fio_enter.month,
                                                  day=fio_enter.day, hour=8, minute=0)
                # обработка обеда если выход раньше 12:00, то обед не учитывается
                if (fio_out > datetime.datetime(year=fio_out.year, month=fio_out.month,
                                                day=fio_out.day, hour=12, minute=0)
                        and fio_out - fio_enter > datetime.timedelta(hours=1)):
                    launch_time = datetime.timedelta(hours=1)
                else:
                    launch_time = datetime.timedelta(hours=0)
                # обработка ночников # TODO добавить автоматический пересчёт вчерашней даты
                if fio_enter > fio_out:
                    nighties.append(fio)
                    skud_day_duration = 0
                    skud_error = True
                else:
                    skud_day_duration = round(((fio_out - fio_enter - launch_time).seconds / 3600) / 0.5, 0) * 0.5
                    skud_error = False
                # охранение результатов
                results_line.update({
                    'fio': fio,
                    'date': date,
                    'skud_day_start_1': fio_enter,
                    'skud_day_end_1': fio_out,
                    'skud_day_duration': skud_day_duration,
                    'skud_error': skud_error
                })
                results.append(results_line.copy())
                # print(fio, skud_day_duration)
    # print(*results)
    # print(exits[1][2]-enters[1][2])
    return results


def skud_tabel_insert(start_date: str = None, end_date: str = None):
    # Получение данных
    data = get_tabel_skud(start_date=start_date, end_date=end_date)
    with session_factory() as session:
        # Получение всех fio и их id из таблицы Employee
        fios = {employee.fio: employee.id for employee in session.execute(select(Employee)).scalars().all()}

        # Подготовка данных для обновления и вставки
        update_data = []
        insert_data = []

        for line in data:

            fio = line.pop('fio')
            fio_id = fios.get(fio)
            date = line.get('date')

            if fio_id:
                # Проверка существования записи с той же датой
                existing_record = session.query(Timesheet).filter(
                    Timesheet.employee_id == fio_id,
                    Timesheet.date == date
                ).first()

                if existing_record:
                    # Подготовка данных для обновления
                    update_data.append({
                        'employee_id': fio_id,
                        'date': date,
                        **line
                    })
                else:
                    # Подготовка данных для вставки
                    line.pop('date')
                    new_record = Timesheet(employee_id=fio_id, date=date, **line)
                    insert_data.append(new_record)
            else:
                # print(f"Person with FIO {fio} not found in the database")
                pass

        # Выполнение пакетного обновления
        if update_data:
            for record in update_data:
                session.execute(
                    update(Timesheet).
                    where(
                        Timesheet.employee_id == record['employee_id'],
                        Timesheet.date == record['date']
                    ).
                    values(**{k: v for k, v in record.items() if k not in ['employee_id', 'date']})
                )
                session.commit()
                # logger.debug(f'Обновлена запись {record} ')
            logger.info(f"Обновлено {len(update_data)} записей")

        # Выполнение пакетной вставки
        if insert_data:
            session.bulk_save_objects(insert_data)
            session.commit()
            logger.info(f"Добавлено {len(insert_data)} записей")

        # if update_data:
        #     session.bulk_update_mappings(Timesheet, update_data)
        # session.commit()
        # session.bulk_save_objects(data_to_update)

    # query = ((select(Timesheet).where(Timesheet.date >= start_time,
    #                                   Timesheet.date <= end_time,
    #                                   Timesheet.skud_day_duration != None
    #                                   # Employee.status == 'явка'
    #                                   ))
    #          .select_from(Employee)
    #          .join(Timesheet, Employee.id == Timesheet.employee_id))

    # print(data)


if __name__ == '__main__':
    st_date = '2024-01-05'
    en_date = '2024-25-05'
    skud_tabel_insert()
    # print(query_execute(query_create('enter', start_date=st_date, end_date=en_date)))
    # get_tabel_skud(start_date=st_date, end_date=en_date)
    # query_create
