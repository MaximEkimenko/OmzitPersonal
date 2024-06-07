import os
from service.data_prepare import DataPrepare
import shutil
from m_logger_settings import logger
from service.xml_to_json import xml_zup_read
from constants import BASEDIR, MODE
from dotenv import load_dotenv

if MODE == 'test':
    from constants import test_dotenv_path as dotenv_path
if MODE == 'docker':
    from constants import dotenv_path as dotenv_path
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def json_creation() -> list:
    """
    Модуль чтения xml исходных данных сохранения их в json файл.
    :return: Список словарей из xml
    """
    # TODO в случае создания UI директории перенести в настройки приложения и передавать функции на входе
    # TODO удалить deprecated функционал
    onec_dir_xml_zup = os.getenv("ONEC_DIR_XML_ZUP")
    onec_dir_json = os.getenv("ONEC_DIR_JSON")
    # директория хранения ЗУП xml 1C
    # onec_dir_xml_zup = r'/personal_app/xml_data'  # для docker
    # onec_dir_xml_zup = r'D:\xml_data'  # для тестов
    # директория хранения переформатированного из xml 1С
    # onec_dir_json = r'/personal_app/xml_data/reformat'  # для docker
    # onec_dir_json = r'D:\xml_data\reformat'  # для тестов
    # файл excel из xml ЗУП 1C
    xlsx_from_xml_zup = os.path.join(onec_dir_json, 'zup_fios_json_1C.xlsx')
    logger.debug(f'файл excel из xml ЗУП 1C {xlsx_from_xml_zup=}')
    # файл json из xml ЗУП 1C
    json_from_xml_zup = os.path.join(onec_dir_json, 'zup_fios_json_1C.json')
    logger.debug(f'файл json из xml ЗУП 1C {json_from_xml_zup=}')
    # файл json из xml ТАБЕЛЯ 1C
    # json_from_xml_tabel = os.path.join(onec_dir_json, 'tabel_fios_json_1C.json')
    # исходный xml файл табеля 1С
    # xml_tabel = r'M:\Xranenie\Reportbolid\Табель\ТабельЕРП(Новый).xml'
    # переформатированный исходник 1С из xml функцией xml_tabel_read
    tabel_fios_json_1C = os.path.join(onec_dir_json, 'tabel_fios_json_1C.json')
    # переформатированный исходник 1С из xml функцией xml_to_xlsx
    zup_fios_json_1C = os.path.join(onec_dir_json, 'zup_fios_json_1C.json')
    logger.debug(f'переформатированный исходник 1С из xml {zup_fios_json_1C=}')
    # директория хранения json python
    # dotenv_path = os.path.join(BASEDIR, '.env')
    # python_dir = r'/json'
    python_dir = os.path.join(BASEDIR, 'json')
    logger.debug(f'директория хранения json python {python_dir=}')
    # создаваемые json табеля для записи в БД python
    tabel_fios_json_python = os.path.join(python_dir, 'tabel_fios_json_python.json')
    zup_fios_json_python = os.path.join(python_dir, 'zup_fios_json_python.json')
    fio_full_json = os.path.join(python_dir, 'fio_full_json.json')
    data_errors_file = os.path.join(python_dir, 'data_errors.json')

    # переформатирование исходного xml ЗУП
    xml_zup_read(xml_path=onec_dir_xml_zup, xlsx_file=xlsx_from_xml_zup, json_file=json_from_xml_zup)

    # словарь перевода ЗУП файла
    zup_fios_translate_dict = {'ФИО': 'fio',
                               'ТабНомер': 'tabel_number',
                               'Статус': 'status',
                               'ГрафикРаботы': 'schedule_1C',
                               'Должность': 'job_title',
                               'Подразделение': 'division_1C',
                               'ДатаПриема': 'employment_date',
                               'ДатаУвольнения': 'fired_date',
                               'ДатаРождения': 'birthday_date',
                               'ФизическоеЛицоИНН': 'INN_employee',
                               'ИННОрганизации': 'INN_company',
                               'Организация': 'company_name',
                               'ВидЗанятости': 'job_type',
                               'ДатаДокумента': 'document_date',
                               'Документ': 'document',
                               'ИсходныйФайл': 'zup_filename'
                               }
    # перевод файла ЗУПА
    try:
        zup_fios = DataPrepare(json_file=zup_fios_json_1C, translate_dict=zup_fios_translate_dict,
                               new_json_file=zup_fios_json_python)
        zup_fios_list = zup_fios.translate_fields()
    except Exception as e:
        logger.error(f'Ошибка очистки данных и формирования zup_fios_list')

    # копирование python jsons в общий доступ
    try:
        # shutil.copy(tabel_fios_json_python, onec_dir_json)
        shutil.copy(zup_fios_json_python, onec_dir_json)
        # shutil.copy(fio_full_json, onec_dir_json)
        # shutil.copy(data_errors_file, onec_dir_json)
        logger.info(f'Копирование файла {tabel_fios_json_python} в директорию {onec_dir_json}, прошло успешно')
    except Exception as e:
        logger.error(f'Ошибка копирования файлов {tabel_fios_json_python}, '
                     f'{zup_fios_json_python}, '
                     # f'{fio_full_json} '
                     f'в директорию {onec_dir_json}, '
                     # f'в директорию {data_errors_file}.'
                     )
        logger.exception(e)
    return zup_fios_list

# переформатирование исходного xml табеля
    # xml_tabel_read(xml_file=xml_tabel, json_file=json_from_xml_tabel)

    # TODO проверить необходимость работы с табелем. Удалить по завершению тестов.
    # словарь перевода табель файла
    # tabel_fios_translate_dict = {'Сотрудник': 'fio',
    #                              'Ответственный': 'fio_responsible',
    #                              'ИННСотрудника': 'INN_employee',
    #                              'ИННОтветственного': 'INN_responsible',
    #                              'ИННОрганизации': 'INN_company',
    #                              }
    # # перевод табеля файла
    # tabel_fios = DataPrepare(json_file=tabel_fios_json_1C, translate_dict=tabel_fios_translate_dict,
    #                          new_json_file=tabel_fios_json_python)
    # tabel_fios_list = tabel_fios.translate_fields()

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
#     # TODO проверить уникальность записей удалить по завршению тестов
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
