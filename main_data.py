import datetime
from service.json_creation import json_creation
from service.clean_data import clean_data
from database.database_crud_operations import bulk_add
from database.database_crud_operations import bulk_update
from database.get_data_from_skud import get_skud_data

# Чтение xml создание json
zup_to_cleaning = json_creation()
# очистка данных
clean_zup_to_python = clean_data(zup_to_cleaning)
# Групповое добавление в БД данных ЗУП в таблицу Employee
bulk_add(clean_zup_to_python)
# Групповое обновление в БД данных ЗУП в таблице Employee
bulk_update(clean_zup_to_python)
# Получение данных табеля и занесение в таблицу Timesheets за вчерашний день
get_skud_data()
# ручная выгрузка интервала из СКУД
# date_string = '2024-03-01'  # дата начала
# random_date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
# today = datetime.datetime.now().date()
# get_skud_data(date_start=random_date, date_end=today)

