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


def python_to_1C(save_json=True):
    """
    :param save_json: Переменная сохранения json
    :return:
    """

    end_date = datetime.datetime.now()
    start_date = datetime.datetime(end_date.year, end_date.month, 1)
    # end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
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
    resp_xml_dir = os.getenv('RESP_DIR')
    # resp_xml_dir = configs['RESP_DIR']
    # resp_xml_dir = '/personal_app/xml_data/responsible/ЕРП.xml'
    responsible_filter_list = get_responsible()
    resp_dict = convert_list_to_dict_with_filter(resp_xml_read(resp_xml_dir), filter_list=responsible_filter_list)
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
        onec_dir_json = os.getenv('ONEC_DIR_JSON')
        # onec_dir_json = configs['ONEC_DIR_JSON']
        # onec_dir_json = '/personal_app/xml_data/reformat'
        json_to_1C_file = os.path.join(onec_dir_json, 'json_to_1C.json')
        json_to_1C = convert_list_to_dict(list_to_1C)

        # преобразование поля _Сотрудник в Сотрудник
        new_list = []
        for person in json_to_1C.values():
            if 'Сотрудник_' in person:
                person['Сотрудник'] = person.pop('Сотрудник_')
            new_list.append(person)
        try:
            with open(json_to_1C_file, 'w', encoding='utf8') as file:
                json.dump(new_list, file, indent=2, ensure_ascii=False)
                logger.info(f'{json_to_1C_file} сохранён.')
        except Exception as e:
            logger.error(f'Ошибка при сохранении {json_to_1C_file}')
            logger.exception(e)
    logger.info(f'Данные для 1С в периоде {start_date} - {end_date} выгружены.')
    return convert_list_to_dict(list_to_1C)


if __name__ == '__main__':
    # tst_start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%d-%m")
    # tst_end_date = (datetime.date.today() + datetime.timedelta(days=10)).strftime("%Y-%d-%m")
    python_to_1C()
