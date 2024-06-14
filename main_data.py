import datetime
from service.json_creation import json_creation
from service.clean_data import clean_data
from database.database_crud_operations import bulk_add
from database.database_crud_operations import bulk_update
from database.get_data_from_skud import get_skud_data
from m_logger_settings import logger
from database.get_data_from_skud_2 import skud_tabel_insert, insert_enters
from database.schedule_calculation import schedule_5_2
from service.python_to_1C import python_to_1C

def schedule_db_refresh(start_date=None, end_date=None):
    """
    Функция выполняет сбор из БД СКУД и запись в БД personal данных с даты start_date до end_date
    :param end_date:
    :param start_date:
    :return:
    """
    try:
        zup_to_cleaning = json_creation()
        logger.info('zup_to_cleaning complete!')
    except Exception as e:
        logger.error('Ошибка zup_to_cleaning')
        logger.exception(e)
    # очистка данных
    try:
        clean_zup_to_python = clean_data(zup_to_cleaning)
        logger.info('clean_zup_to_python complete!')
    except Exception as e:
        logger.error('Ошибка clean_zup_to_python')
        logger.exception(e)
    # Групповое добавление в БД данных ЗУП в таблицу Employee
    try:
        bulk_add(clean_zup_to_python)
        logger.info('bulk_add complete!')
    except Exception as e:
        logger.error('Ошибка bulk_add')
        logger.exception(e)
    # Групповое обновление в БД данных ЗУП в таблице Employee
    try:
        bulk_update(clean_zup_to_python)
        logger.info('bulk_update complete!')
    except Exception as e:
        logger.error('Ошибка bulk_update')
        logger.exception(e)
    if not all((start_date, end_date)):
        # Получение данных табеля и занесение в таблицу Timesheets за вчерашний день
        try:
            access_points = ('122', '312', 'Турникет')
            for access_point in access_points:
                skud_tabel_insert(access_point=access_point)
                insert_enters(access_point=access_point)
            logger.info('Загрузка в БД personal за вчерашний день выполнена.')
        except Exception as e:
            logger.error('Ошибка при загрузке в БД personal за вчерашний день.')
            logger.exception(e)
    else:
        # Получение данных табеля и занесение в таблицу Timesheets за период
        try:
            access_points = ('122', '312', 'Турникет')
            for access_point in access_points:
                skud_tabel_insert(start_date=start_date, end_date=end_date, access_point=access_point)
                insert_enters(access_point=access_point)
                # TODO сделать только 1 раз при полном добавлении, либо сделать одним запросом
                # schedule_5_2()  # заполнение выходных при графике 5/2
            # get_skud_data(date_start=start_date, date_end=end_date)
            logger.info(f"Загрузка в БД personal за период {start_date} - {end_date} выполнена.")
        except Exception as e:
            logger.error(f'Ошибка при загрузке в БД personal за период за период {start_date} - {end_date}.')
            logger.exception(e)
    # python_to_1C(start_date=start_date, end_date=end_date)


if __name__ == '__main__':
    end_date_tst = (datetime.date.today() + datetime.timedelta(days=10)).strftime("%Y-%d-%m")
    start_date_tst = (datetime.date.today() - datetime.timedelta(days=10)).strftime("%Y-%d-%m")

    schedule_db_refresh(start_date=start_date_tst, end_date=end_date_tst)


