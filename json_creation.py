import os
import json
from utils.data_prepare import DataPrepare
import shutil
from m_logger_settings import logger
from utils.xml_to_json import xml_zup_read
from utils.xml_to_json import xml_tabel_read

"""
Модуль подготовки данных в json формат из исходных xml 1C файлов 
Модуль запускается по расписанию
"""
# TODO в случае создания UI директории перенести в настройки приложения
# директория хранения ЗУП xml 1C
onec_dir_xml_zup = r'M:\Xranenie\Reportbolid'
# директория хранения переформатированного из xml 1С
onec_dir_json = r'M:\Xranenie\Reportbolid\reformat'
# файл excel из xml ЗУП 1C
xlsx_from_xml_zup = os.path.join(onec_dir_json, 'zup_fios_json_1C.xlsx')
# файл json из xml ЗУП 1C
json_from_xml_zup = os.path.join(onec_dir_json, 'zup_fios_json_1C.json')
# файл json из xml ТАБЕЛЯ 1C
json_from_xml_tabel = os.path.join(onec_dir_json, 'tabel_fios_json_1C.json')
# исходный xml файл табеля 1С
xml_tabel = r'M:\Xranenie\Reportbolid\Табель\ТабельЕРП(Новый).xml'
# переформатированный исходник 1С из xml функцией xml_tabel_read
tabel_fios_json_1C = os.path.join(onec_dir_json, 'tabel_fios_json_1C.json')
# переформатированный исходник 1С из xml функцией xml_to_xlsx
zup_fios_json_1C = os.path.join(onec_dir_json, 'zup_fios_json_1C.json')
# директория хранения json python
python_dir = r'D:\АСУП\Python\Projects\OmzitPersonal\json'
# создаваемые json табеля для записи в БД python
tabel_fios_json_python = os.path.join(python_dir, 'tabel_fios_json_python.json')
zup_fios_json_python = os.path.join(python_dir, 'zup_fios_json_python.json')
fio_full_json = os.path.join(python_dir, 'fio_full_json.json')
data_errors_file = os.path.join(python_dir, 'data_errors.json')

# переформатирование исходного xml ЗУП
xml_zup_read(xml_path=onec_dir_xml_zup, xlsx_file=xlsx_from_xml_zup, json_file=json_from_xml_zup)
# переформатирование исходного xml табеля
xml_tabel_read(xml_file=xml_tabel, json_file=json_from_xml_tabel)

# словарь перевода табель файла
tabel_fios_translate_dict = {'Сотрудник': 'fio',
                             'Ответственный': 'fio_responsible',
                             'ИННСотрудника': 'INN_employee',
                             'ИННОтветственного': 'INN_responsible',
                             'ИННОрганизации': 'INN_company',
                             }
# перевод табеля файла
tabel_fios = DataPrepare(json_file=tabel_fios_json_1C, translate_dict=tabel_fios_translate_dict,
                         new_json_file=tabel_fios_json_python)
tabel_fios_list = tabel_fios.translate_fields()
# словарь перевода ЗУП файла
zup_fios_translate_dict = {'ФИО': 'fio',
                           'ТабНомер': 'tabel_number',
                           'Статус': 'status',
                           'ГрафикРаботы': 'schedule',
                           'Должность': 'job_title',
                           'Подразделение': 'division',
                           'ДатаПриема': 'employment_date',
                           'ДатаУвольнения': 'fired_date',
                           'ДатаРождения': 'birthday_date',
                           'ФизическоеЛицоИНН': 'INN_employee',
                           'ОрганизацияИНН': 'INN_company',
                           'ИсходныйФайл': 'tabel_filename'
                           }
# перевод файла табеля
zup_fios = DataPrepare(json_file=zup_fios_json_1C, translate_dict=zup_fios_translate_dict,
                       new_json_file=zup_fios_json_python)
zup_fios_list = zup_fios.translate_fields()

"""
Первоначально смотрится файл ЗУП: zup_fios_list. Чистятся повторы мусор и возвращается 
в zup_to_pyhon.json для занесения в БД.
"""
zup_to_python = ''
"""

"""


# # ОБЪЕДИНЕНИЕ НЕ НУЖНО!
# # объединение ЗУП и ТАБЕЛЯ в 1 json
# data_errors_list = []  # список ФИО ошибок
# filtered_keys = ['fio', 'INN_employee', 'INN_company']  # ключи для файла ошибок
# full_data_list = []
# # разрешённые статусы
# # allowed_statuses = ('Работа', 'ОтпускОсновной', 'ОтпускНеоплачиваемыйПоРазрешениюРаботодателя')
# # формирование словаря по ФИО из ЗУПА
# dict_by_fio_from_zup = {d['fio']: d for d in zup_fios_list}
# for tabel_line in tabel_fios_list:
#     # TODO проверить уникальность записей
#     if (tabel_line['fio'] in dict_by_fio_from_zup
#             and dict_by_fio_from_zup[tabel_line['fio']]['INN_employee'] == tabel_line['INN_employee']
#             # and dict_by_fio_from_zup[tabel_line['fio']]['tabel_number'] == tabel_line['tabel_number']
#        ):
#         full_data_dict = tabel_line.copy()
#         full_data_dict.update(dict_by_fio_from_zup[tabel_line['fio']])
#         full_data_list.append(full_data_dict)
#     else:
#         data_errors_list.append({k: tabel_line.get(k) for k in filtered_keys})
#         logger.warning(f"Сотрудник {tabel_line['fio']} не попал в общий список сотрудников."
#                        f"ИНН сотрудника: {tabel_line['INN_employee']} "
#                        f"ИНН компании {tabel_line['INN_company']}")
# # сохранение полного json табеля и ЗУПА
# try:
#     with open(fio_full_json, 'w', encoding='utf-8') as json_file:
#         json.dump(full_data_list, json_file, indent=2, ensure_ascii=False)
#         logger.info(f"Полный файл JSON {fio_full_json} сохранён успешно.")
# except Exception as e:
#     logger.error(f"Ошибка сохранения {fio_full_json}.")
#     logger.exception(e)
# # сохранение json ошибок
# if data_errors_file:
#     try:
#         with open(data_errors_file, 'w', encoding='utf-8') as json_file:
#             json.dump(data_errors_list, json_file, indent=2, ensure_ascii=False)
#         logger.info(f"Файл ошибок данных {data_errors_file} сохранён успешно.")
#     except Exception as e:
#         logger.error(f"Ошибка сохранения {data_errors_file}.")
#         logger.exception(e)

# копирование python jsons в общий доступ
try:
    shutil.copy(tabel_fios_json_python, onec_dir_json)
    shutil.copy(zup_fios_json_python, onec_dir_json)
    # shutil.copy(fio_full_json, onec_dir_json)
    # shutil.copy(data_errors_file, onec_dir_json)
except Exception as e:
    logger.error(f'Ошибка копирования файлов {tabel_fios_json_python}, '
                 f'{zup_fios_json_python}, '
                 # f'{fio_full_json} '
                 f'в директорию {onec_dir_json}, '
                 # f'в директорию {data_errors_file}.'
                 )
    logger.exception(e)
