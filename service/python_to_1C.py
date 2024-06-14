import json
import os
import datetime
from copy import copy
from m_logger_settings import logger

from dotenv import dotenv_values

from sqlalchemy import select

from database.database import session_factory

from database.models import Employee, Timesheet
from constants import MODE

from dotenv import load_dotenv

if MODE == 'test':
    from constants import test_dotenv_path as dotenv_path
if MODE == 'docker':
    from constants import dotenv_path as dotenv_path
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    configs = dotenv_values(dotenv_path)


def python_to_1C(start_date: datetime.datetime, end_date: datetime.datetime, save_json=True):
    """
    :param start_date: начало периода выгрузки
    :param end_date: окончание периода выгрузки
    :param save_json: Переменная сохранения json
    :return:
    """
    dict_to_1C = dict()
    list_to_1C = []
    # получить весь Timesheet за период
    query = ((select(Timesheet).where(Timesheet.date >= start_date,
                                      Timesheet.date <= end_date,
                                      Timesheet.skud_day_duration != None
                                      # Employee.status == 'явка'
                                      ))
             .select_from(Employee)
             .join(Timesheet, Employee.id == Timesheet.employee_id))
    with session_factory() as session:
        result = session.execute(query)
        timesheets = result.scalars().all()
        for timesheet in timesheets:
            dict_to_1C.clear()
            dict_to_1C['Сотрудник'] = timesheet.employee.fio
            dict_to_1C['ИННСотрудника'] = timesheet.employee.INN_employee
            dict_to_1C['ИННОрганизации'] = timesheet.employee.INN_company
            if timesheet.skud_day_duration:
                dict_to_1C[f'Число{timesheet.date.day}'] = timesheet.skud_day_duration
            elif timesheet.day_status_short != 'Я':
                dict_to_1C[f'Число{timesheet.date.day}'] = timesheet.day_status_short
            if timesheet.skud_night_duration:
                dict_to_1C[f'Число{timesheet.date.day}Ночные'] = timesheet.skud_night_duration
            list_to_1C.append(copy(dict_to_1C))

    def convert_list_to_dict(data):
        """
        Преобразование списка в словарь
        :param data:
        :return:
        """
        dict_to_1C = {}
        for item in data:
            fio = item['Сотрудник']
            if fio in dict_to_1C:
                for key, value in item.items():
                    if key != 'Сотрудник':
                        if key not in dict_to_1C[fio]:
                            dict_to_1C[fio][key] = str(value)
            else:
                dict_to_1C[fio] = {}
                for key, value in item.items():
                    if key != 'Сотрудник':
                        dict_to_1C[fio][key] = str(value)
        return dict_to_1C


    # сохранение в файле json_to_1C.json
    if save_json:
        onec_dir_json = configs['ONEC_DIR_JSON']
        json_to_1C_file = os.path.join(onec_dir_json, 'json_to_1C.json')
        json_to_1C = convert_list_to_dict(list_to_1C)
        with open(json_to_1C_file, 'w') as file:
            json.dump(json_to_1C, file, indent=2, ensure_ascii=False)
            logger.info(f'{json_to_1C_file} сохранён.')
    logger.info(f'Данные для 1С в периоде {start_date} - {end_date} выгружены.')
    return convert_list_to_dict(list_to_1C)


if __name__ == '__main__':
    tst_start_date = datetime.datetime(2024, 6, 1)
    tst_end_date = datetime.datetime(2024, 6, 15)
    python_to_1C(start_date=tst_start_date, end_date=tst_end_date)
