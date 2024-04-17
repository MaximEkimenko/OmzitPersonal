from copy import copy, deepcopy
import jmespath

from utils.data_prepare import DataPrepare
import os

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

zup_fios = DataPrepare(json_file=zup_fios_json_1C, translate_dict=zup_fios_translate_dict,
                       new_json_file=zup_fios_json_python)
zup_fios_list = zup_fios.translate_fields()

allowed_statuses = (
    'Работа', 'ОтпускОсновной', 'ОтпускНеоплачиваемыйПоРазрешениюРаботодателя', 'ОтпускПоУходуЗаРебенком')
dict_by_fio_from_zup = {d['fio']: d for d in zup_fios_list if d['status'] in allowed_statuses}
# print(dict_by_fio_from_zup)


# machines[?state=='running'].name
# tabel_fios_list =
# print(jmespath.search('[?"2024-03-01" != "0"]', tabel_fios_list))
# for d in tabel_fios_list:
#     print(jmespath.search('length(fio)', d))



# date_key_list = []
# unique_fios = set([d['fio'] for d in tabel_fios_list])
unique_fios = ("Мокроусова Ольга Игоревна", )
# unique_days = set()
result_dict = dict()
dicts = []
a = dict()
for d in tabel_fios_list:
    if d['fio'] in unique_fios:
        print(d)
# for d in tabel_fios_list:
#     if d['fio'] in unique_fios:
#         for key in d:
#             if d[key] != "":
#                 print(f'{key}: {d[key]}')
#     for k in d:
#         if 'day_status' in k:
#             unique_days.add(k)
#
#
# # print(unique_fios)
# # print(sorted(list(unique_days)))
#
# fios_list = []
# for d in tabel_fios_list:
#     if d['fio'] in unique_fios:
#         print(d['fio'])
#         for day in unique_days:
#             if d.get(day, '') != '':
#                 print(f'{day} : {d[day]}')
        # print(d['fio'])
        # print(d['2024-03-18_day_status'])
        # for key, value in d.items():
        #     if value != '' and 'hours' not in key:
        #         print(f'{key} : {value} ')
            # if 'day_status' in key and value != '':
            #     print(f'{key} : {value} ')
            # if 'hours' in key:
            #     print(f'{key} : {value} ')
            # # else:
            #     print(f'{key} : {value}')
            # if key in date_key_list and value == '':
            #     continue
        #     new_dict[key] = copy(d[key])
        # fios_list.append(copy(new_dict))
# print(fios_list)
# print(d)
# print(new_new_dict)
