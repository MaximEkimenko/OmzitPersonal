import datetime
import json
import os.path
from copy import copy
from typing import Optional, List
import shutil


class DataPrepare:
    """
    класс подготовки данных из json 1C в БД
    """

    def __init__(self, translate_dict: dict, json_file: str, new_json_file):
        """

        :param translate_dict: словарь переводчик полей json в поля БД
        :param json_file: json файл с данными 1С
        """
        self.json_file = json_file
        self.new_json_file = new_json_file
        self.translate_dict = translate_dict
        self.json_data = self._json_read(self.json_file)

    @staticmethod
    def _json_read(json_file):
        """
        Открытие json файла
        :param json_file:
        :return:
        """
        with open(json_file, 'r', encoding='utf8') as file:
            return json.load(file)

    @staticmethod
    def _json_write(new_json_file, data):
        """
        Сохранение json файла
        :param new_json_file:
        :return:
        """
        with open(new_json_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)

    def translate_fields(self):
        """
        Перевод полей json в поля БД
        :return: dict
        """
        result_dict = {}
        result_list = []
        for line in self.json_data:
            # определение даты для файла табеля
            if line.get('НачалоПериода'):
                date_from_str = datetime.datetime.strptime(line.get('НачалоПериода'), '%d.%m.%Y %H:%M:%S')
                month = date_from_str.strftime('%m')
                year = date_from_str.strftime('%Y')
            else:
                month = ''
                year = ''
            for key, value in line.items():
                if self.translate_dict.get(key) is not None or 'Число' in key or 'Часов' in key:
                    if 'Число' in key:
                        try:
                            date = datetime.datetime.strptime(f'{key[5:]}.{month}.{year}', '%d.%m.%Y').date()
                            result_dict.update({f"{date}_day_status": value})
                        except ValueError:
                            pass
                    elif 'Часов' in key:
                        try:
                            date = datetime.datetime.strptime(f'{key[5:]}.{month}.{year}', '%d.%m.%Y').date()
                            result_dict.update({f"{date}_hours": value})
                        except ValueError:
                            pass
                    else:
                        result_dict.update({self.translate_dict.get(key): value})
            result_list.append(copy(result_dict))
        # сохранение нового json
        self._json_write(self.new_json_file, data=result_list)
        return result_list


if __name__ == '__main__':
    # новый json табеля
    # shutil.copy("D:\\test.txt", "D:\\folder")
    onec_dir = r'M:\Xranenie\Reportbolid\reformat'
    python_dir = r'D:\АСУП\Python\Projects\OmzitPersonal\json'
    tabel_fios_json_1C = os.path.join(onec_dir, 'tabel_fios_json_1C.json')
    tabel_fios_json_python = os.path.join(python_dir, 'tabel_fios_json_python.json')
    zup_fios_json_1C = os.path.join(onec_dir, 'zup_fios_json_1C.json')
    zup_fios_json_python = os.path.join(python_dir, 'zup_fios_json_python.json')

    tabel_fios_translate_dict = {'Сотрудник': 'fio',
                                 'Ответственный': 'fio_responsible',
                                 'ИННСотрудника': 'INN_employee',
                                 'ИННОтветственного': 'INN_responsible',
                                 'ИННОрганизации': 'INN_company',
                                 }
    tabel_fios = DataPrepare(json_file=tabel_fios_json_1C, translate_dict=tabel_fios_translate_dict,
                             new_json_file=tabel_fios_json_python)
    tabel_fios_list = tabel_fios.translate_fields()
    # новый json зупа
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
    zup_fios = DataPrepare(json_file=zup_fios_json_1C, translate_dict=zup_fios_translate_dict,
                           new_json_file=zup_fios_json_python)
    zup_fios_list = zup_fios.translate_fields()
    # shutil.copy(tabel_fios_json_python, onec_dir)
    # shutil.copy(zup_fios_json_python, onec_dir)

    # for line in zup_fios_list:
    #     for key, val in line.items():
    #         if key == 'fio' and val == 'Шкапов Дмитрий Александрович':
    #             print(f"{val}:{line['tabel_filename']} {line['INN_company']} {line['tabel_number']}")
    # объединение списков в список табеля
    full_data_list = []
    dict_by_fio_from_zup = {d['fio']: d for d in zup_fios_list}  # формирование словаря по ФИО из ЗУПА
    print(dict_by_fio_from_zup)
    for tabel_line in tabel_fios_list:
        if (tabel_line['fio'] in dict_by_fio_from_zup
                and dict_by_fio_from_zup[tabel_line['fio']]['INN_company'] == tabel_line['INN_company']):
            full_data_dict = tabel_line.copy()
            full_data_dict.update(dict_by_fio_from_zup[tabel_line['fio']])
            full_data_list.append(full_data_dict)
        else:
            # full_data_list.append(tabel_line)
            print('!!!!!!!!!!', tabel_line['fio'])
            # print(dict_by_fio_from_zup[tabel_line['fio']]['INN_company'], tabel_line['INN_company'])

    # print(new_list)
    # for zup_line in zup_fios_list:
    #     for tabel_line in tabel_fios_list:
    #         if zup_line['INN_company'] == tabel_line['INN_company']:
    #             a = tabel_line | zup_line
    #             # new_list.append(copy(tabel_line))
    #             print(tabel_line['fio'])
    #             new_list.append(copy(a))
    #             break
    #         else:
    #             continue

    # print(tabel_fios_list)
    fio_full_json = r'D:\АСУП\Python\Projects\OmzitPersonal\json\fio_full_json.json'

    # for tabel_line in tabel_fios_list:
    #     for zup_line in zup_fios_list:
    #         if tabel_line['INN_company'] == zup_line['INN_company']:
    #             tabel_line.update(copy(zup_line))
    #             # print(zup_line['fio'])
    # # print(tabel_fios_list)
    # fio_full_json = r'fio_full_json.json'
    with open(fio_full_json, 'w', encoding='utf-8') as json_file:
        json.dump(full_data_list, json_file, indent=2, ensure_ascii=False)


    # print(fios_tabel_json)
    # print(a._json_read(r'D:\АСУП\Python\Projects\OmzitPersonal\json\fios_tabel.json'))
