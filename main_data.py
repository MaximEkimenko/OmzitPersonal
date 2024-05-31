import datetime
from service.json_creation import json_creation
from service.clean_data import clean_data
from database.database_crud_operations import bulk_add
from database.database_crud_operations import bulk_update
from database.get_data_from_skud import get_skud_data
from m_logger_settings import logger
from database.get_data_from_skud_2 import skud_tabel_insert


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
            skud_tabel_insert()
            # get_skud_data()
            logger.info('Загрузка в БД personal за вчерашний день выполнена.')
        except Exception as e:
            logger.error('Ошибка при загрузке в БД personal за вчерашний день.')
            logger.exception(e)
    else:
        # Получение данных табеля и занесение в таблицу Timesheets за период
        try:
            get_skud_data(date_start=start_date, date_end=end_date)
            logger.info(f"Загрузка в БД personal за период {start_date} - {end_date} выполнена.")
        except Exception as e:
            logger.error(f'Ошибка при загрузке в БД personal за период за период {start_date} - {end_date}.')
            logger.exception(e)



    #
    #
    #
    # # Чтение xml создание json
    # zup_to_cleaning = json_creation()
    # # очистка данных
    # clean_zup_to_python = clean_data(zup_to_cleaning)
    # # Групповое добавление в БД данных ЗУП в таблицу Employee
    # bulk_add(clean_zup_to_python)
    # # Групповое обновление в БД данных ЗУП в таблице Employee
    # bulk_update(clean_zup_to_python)
    # get_skud_data()
    # # ручная выгрузка интервала из СКУД
    # date_string = '2024-05-01'  # дата начала
    # random_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
    # today = datetime.datetime.now().date()
    # get_skud_data(date_start=random_date, date_end=today)
    #


if __name__ == '__main__':
    end_date_tst = datetime.date.today()
    schedule_db_refresh(start_date=datetime.date(year=2024, day=1, month=5), end_date=end_date_tst)


