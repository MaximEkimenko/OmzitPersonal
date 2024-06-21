import json
import os
import datetime
from copy import copy
from pprint import pprint

from m_logger_settings import logger
from service.xml_to_json import resp_xml_read
from dotenv import dotenv_values

from sqlalchemy import select
from database.database import session_factory
from database.database_crud_operations import get_responsible

from database.models import Employee, Timesheet
from constants import MODE
from service.tools import convert_list_to_dict, convert_list_to_dict_with_filter
from dotenv import load_dotenv

if MODE == 'test':
    from constants import test_dotenv_path as dotenv_path
if MODE == 'docker':
    from constants import dotenv_path as dotenv_path
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    configs = dotenv_values(dotenv_path)


def python_to_1C(start_date: str, end_date: str, save_json=True):
    """
    :param start_date: начало периода выгрузки
    :param end_date: окончание периода выгрузки
    :param save_json: Переменная сохранения json
    :return:
    """

    # переопределение дат
    # start_date = datetime.datetime.strptime(start_date, '%Y-%d-%m')
    end_date = datetime.datetime.strptime(end_date, '%Y-%d-%m')
    start_date = datetime.datetime(end_date.year, end_date.month, 1)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
    # получение словаря сотрудников
    query = ((select(Employee).where(Employee.status == 'явка'))
             .select_from(Employee))
    with session_factory() as session:
        result = session.execute(query)
        employees = result.scalars().all()
    # получение словаря Timesheet
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
    # получение словаря ответственных
    resp_xml_dir = configs['RESP_DIR']
    responsible_filter_list = get_responsible()
    # resp_dict = convert_list_to_dict(resp_xml_read(resp_xml_dir))
    # print(responsible_filter_list)
    resp_dict = convert_list_to_dict_with_filter(resp_xml_read(resp_xml_dir), filter_list=responsible_filter_list)


    pprint(resp_dict)




    with session_factory() as session:
        result = session.execute(query)
        timesheets = result.scalars().all()
        for timesheet in timesheets:


            # заполнение данных ответственных
            if resp_dict.get(timesheet.employee.fio):
                dict_to_1C.clear()
                dict_to_1C['Сотрудник'] = timesheet.employee.fio
                dict_to_1C['Сотрудник_'] = timesheet.employee.fio  # поле дублирования сотрудника в json 1C
                dict_to_1C['ИННСотрудник'] = timesheet.employee.INN_employee
                dict_to_1C['ИННОрганизации'] = timesheet.employee.INN_company
                dict_to_1C['Подразделение'] = timesheet.employee.division
                dict_to_1C['Ответственный'] = resp_dict[timesheet.employee.fio].get('Ответственный')
                dict_to_1C['ИННОтветственный'] = resp_dict[timesheet.employee.fio]['ИННОтветственный']
                dict_to_1C['КонецПериода'] = ''
                dict_to_1C['НачалоПериода'] = ''
            # dict_to_1C['Ответственный'] = timesheet.employee.fio_responsible
            # dict_to_1C['ИННОтветственного'] = timesheet.employee.INN_responsible

                dict_to_1C[f'Число{timesheet.date.day}'] = timesheet.day_status_short
                dict_to_1C[f'Часы{timesheet.date.day}'] = timesheet.skud_day_duration

            # if timesheet.skud_day_duration:
            #     dict_to_1C[f'Число{timesheet.date.day}'] = timesheet.skud_day_duration
            # elif timesheet.day_status_short != 'Я':
            #     dict_to_1C[f'Число{timesheet.date.day}'] = timesheet.day_status_short
                if timesheet.skud_night_duration:
                    dict_to_1C[f'Число{timesheet.date.day}Ночные'] = timesheet.skud_night_duration
                list_to_1C.append(copy(dict_to_1C))

    # сохранение в файле json_to_1C.json
    if save_json:
        onec_dir_json = configs['ONEC_DIR_JSON']
        json_to_1C_file = os.path.join(onec_dir_json, 'json_to_1C.json')
        json_to_1C = convert_list_to_dict(list_to_1C)
        # преобразование поля _Сотрудник в Сотрудник
        new_list = []
        for person in json_to_1C.values():
            if 'Сотрудник_' in person:
                person['Сотрудник'] = person.pop('Сотрудник_')
            new_list.append(person)

        with open(json_to_1C_file, 'w', encoding='utf8') as file:
            # json.dump(list_to_1C, file, indent=2, ensure_ascii=False)
            # json.dump(list(json_to_1C.values()), file, indent=2, ensure_ascii=False)
            json.dump(new_list, file, indent=2, ensure_ascii=False)
            logger.info(f'{json_to_1C_file} сохранён.')
    logger.info(f'Данные для 1С в периоде {start_date} - {end_date} выгружены.')
    # print(list_to_1C)
    # return list_to_1C
    return convert_list_to_dict(list_to_1C)


if __name__ == '__main__':
    # tst_start_date = datetime.datetime(2024, 6, 1)
    # tst_end_date = datetime.datetime(2024, 6, 15)
    tst_start_date = '2024-10-6'
    tst_end_date = '2024-19-6'

    python_to_1C(start_date=tst_start_date, end_date=tst_end_date)
