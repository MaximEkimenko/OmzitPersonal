import math

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
        condition_latecomers_800 = f"""WHERE (pLogData.TimeVal >= '{time_day_start_800}')
                    AND dbo.pLogData.Remark like '%{access_point}%' 
                    AND dbo.pLogData.Remark like '%{is_enter}%' """
        order_by = 'DESC'
    elif query_type == 'late_830':
        condition_latecomers_830 = f"""WHERE (pLogData.TimeVal >= '{time_day_start_830}')
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
    return query


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


def get_tabel_skud(start_date: str = None, end_date: str = None) -> list:
    """
    Обработка данных, получение табеля СКУД в интервале start_date end_date
    :param start_date:
    :param end_date:
    :return: список результатов
    """
    results_line = dict()  # словарь строки результата
    # получение данных
    enters = query_execute(query_create('enter', start_date, end_date))
    outs = query_execute(query_create('exit', start_date, end_date))
    nighties = []  # список возможных ночников
    results = []  # список результатов
    # определение длительности работы
    for enter in enters:
        fio = enter[4]  # ФИО
        fio_enter = enter[2]  # вход для fio
        date = datetime.datetime(year=fio_enter.year, month=fio_enter.month, day=fio_enter.day,
                                 hour=0, minute=1)
        # время начала работы # TODO ВЫНЕСТИ В ПАРЕМЕТРЫ
        work_time_start = datetime.datetime(year=fio_enter.year, month=fio_enter.month,
                                            day=fio_enter.day, hour=8, minute=0)
        for out in outs:
            if enter[4] == out[4] and enter[2].day == out[2].day:
                fio_out = out[2]  # выход для fio
                # обработка ночников и ошибок входа
                if fio_out < fio_enter or fio_out < work_time_start:
                    nighties.append(fio)
                    skud_day_duration = 0
                    skud_error = True
                else:
                    # обработка обеда если выход раньше 12:00, то обед не учитывается
                    if fio_out - fio_enter > datetime.timedelta(hours=1):
                        launch_time = datetime.timedelta(hours=1)
                    else:
                        launch_time = datetime.timedelta(hours=0)
                    if fio_enter > work_time_start:  # опоздания
                        late_value = math.floor((fio_enter - work_time_start).seconds/3600)
                    else:
                        late_value = 0
                    skud_day_duration = math.floor((fio_out - fio_enter - launch_time).seconds/3600)
                    skud_error = False

                # сохранение результатов
                results_line.update({
                    'fio': fio,
                    'date': date,
                    'skud_day_start_1': fio_enter,
                    'skud_day_end_1': fio_out,
                    'skud_day_duration': skud_day_duration,
                    'skud_error': skud_error,
                    'late_value': late_value

                })
                results.append(results_line.copy())
    return results


def skud_tabel_insert(start_date: str = None, end_date: str = None):
    """
    Функция добавляет/обновляет данные из СКУД в указанном интервале
    :param start_date:
    :param end_date:
    :return:
    """
    # Получение данных табеля
    data = get_tabel_skud(start_date=start_date, end_date=end_date)
    with session_factory() as session:
        # Получение всех fio и их id из таблицы Employee
        fios = {employee.fio: employee.id for employee in session.execute(select(Employee)).scalars().all()}
        # Подготовка данных табеля для обновления и вставки
        update_data = []
        insert_data = []
        # вставка данных табеля
        for line in data:
            fio = line.pop('fio')
            fio_id = fios.get(fio)
            date = line.get('date')
            if fio_id:
                # Проверка существования записи с той же датой
                existing_record = session.query(Timesheet).filter(
                    Timesheet.employee_id == fio_id, Timesheet.date == date
                ).first()
                if existing_record:
                    # Подготовка данных для обновления
                    update_data.append({
                        'employee_id': fio_id, 'date': date, **line
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
                if record.get('skud_day_end_1', None):  # обновляем только если был выход
                    # print(record)
                    session.execute(
                        update(Timesheet).
                        where(Timesheet.employee_id == record['employee_id'],
                              Timesheet.date == record['date']
                              ).
                        values(**{k: v for k, v in record.items() if k not in ['employee_id', 'date']})
                    )
                else:
                    logger.info(f"Данные выхода {record['skud_day_end_1']} для "
                                f"{record['fio']} не обновились")
            session.commit()
            # logger.debug(f'Обновлена запись {record} ')
            logger.info(f"Обновлено {len(update_data)} записей")

        # Выполнение пакетной вставки
        if insert_data:
            session.bulk_save_objects(insert_data)
            session.commit()
            logger.debug(f"Заполнены данные: {insert_data}")
            logger.info(f"Добавлено {len(insert_data)} записей")


def insert_enters(enters: list = None):
    """
    Функция выполняет первоначальную вставку fio в БД
    :param enters:
    :return:
    """
    start_date = (datetime.date.today()).strftime("%Y-%d-%m")
    end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%d-%m")
    insert_data = []
    if not enters:
        enters = query_execute(query_create('enter', start_date=start_date, end_date=end_date))
    with session_factory() as session:
        # Получение всех fio и их id из таблицы Employee
        fios = {employee.fio: employee.id for employee in session.execute(select(Employee)).scalars().all()}
        for line in enters:
            fio = line[4]
            fio_id = fios.get(fio)
            enter_datetime = line[2]
            work_time_start = datetime.datetime(year=enter_datetime.year, month=enter_datetime.month,
                                                day=enter_datetime.day, hour=8, minute=0)

            if enter_datetime > work_time_start:
                late_value = (enter_datetime - work_time_start).seconds / 60
            else:
                late_value = 0

            date = datetime.datetime(year=enter_datetime.year, month=enter_datetime.month, day=enter_datetime.day,
                                     hour=0, minute=1)
            existing_record = session.query(Timesheet).filter(
                Timesheet.employee_id == fio_id, Timesheet.date == date
            ).first()
            if existing_record:
                logger.debug(f'Запись для {existing_record.employee.fio} в дате {date} уже существует')
            else:
                if fio_id:
                    new_record = Timesheet(employee_id=fio_id, date=date, skud_day_start_1=enter_datetime,
                                           late_value=late_value)
                    insert_data.append(new_record)
        session.bulk_save_objects(insert_data)
        session.commit()
        logger.debug(f"Заполнены данные: {insert_data}")
        logger.info(f"Добавлено {len(insert_data)} записей")

    # print(insert_data)
    # print(fios)
    # print(enters)


def get_latecomers(date: str = None, late_time: str = '08:01'):
    """
    Функция получает список опоздавших на дату
    :return:
    """
    today = datetime.date.today()
    if not date:
        date = datetime.datetime(year=today.year, month=today.month,
                                 day=today.day, hour=int(late_time.split(':')[0]),
                                 minute=int(late_time.split(':')[1]), second=0)
    else:
        date = datetime.datetime.strptime('date', '%d.%m.%Y')
    # обновление БД OmzitPersonal
    start_date = (datetime.date.today()).strftime("%Y-%d-%m")
    end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%d-%m")
    skud_tabel_insert(start_date=start_date, end_date=end_date)
    insert_enters()
    # Получение списка опоздавших из БД OmzitPersonal
    with session_factory() as session:
        res = session.query(Timesheet).where(Timesheet.skud_day_start_1 >= date)
        late_comers = [{'fio': row.employee.fio,
                        'day_start': row.skud_day_start_1,
                        'late_value': round((row.skud_day_start_1 - date).seconds / 60, 0),
                        'division': row.employee.division} for row in res]

    return late_comers
    # print(len(late_comers))
    # print(late_comers)

    # print(res)
    # print(res)
    # print(late_comers)

    # Фиксация опоздавших?
    # Получение списка из СКУД
    # data = query_execute(query_create('late_800'))
    # print(data)


if __name__ == '__main__':
    # get_latecomers()
    insert_enters()
    # get_latecomers()
    st_date = '2024-01-05'
    en_date = '2024-01-06'
    skud_tabel_insert(start_date=st_date, end_date=en_date)
    # skud_tabel_insert()
    # print(get_latecomers(late_time='08:01'))
    pass
