import xml.etree.ElementTree as element_tree
import json
from copy import copy

from openpyxl import Workbook
import os


def xml_accumulate(xml_path: str) -> list:
    """
    Функция возвращает список всех элементов из всех xml файлов в директории xml_path
    :param xml_path:
    :return: list
    """
    file_list = []
    for root_dir, path_dirs, path_files in os.walk(xml_path):
        for file in path_files:
            if '.xml' in file and '~' not in file:
                if xml_path == root_dir:
                    file_list.append(file)
    all_roots = []
    for file in file_list:
        file_path = os.path.join(xml_path, file)
        tree = element_tree.parse(file_path)
        root_xmls = tree.getroot()
        for xml_element in root_xmls:
            xml_element.set('file', file)  # добавление имени файла в элемент
            all_roots.append(xml_element)
    return all_roots


def xml_to_xlsx(xml_path: str, xlsx_file: str = None, json_file: str = None) -> False or dict:
    # TODO добавить директории сохранения файлов xlsx_file json_file в код
    """
    Функция прообразует все файлы xml из директории xml_path в xlsx и json
    :param xml_path: пут ьк директории xml
    :param json_file:  путь к json файлу
    :param xlsx_file: путь к xlsx
    :return: словарь вида {ФИО: {поле: значение}}
    """
    # TODO подключить pandas для работы с xlsx
    wb = Workbook()
    ws = wb.active
    # получение списка всех xml
    # TODO переопределить all_roots для случая ручного ввода имен файлов
    try:
        all_roots = xml_accumulate(xml_path)
    except Exception as e:
        print(e, ' !xml read problem!')
        return False
    # количество полей
    uniq_fields = set()
    for uniq_field in all_roots:
        uniq_fields.add(uniq_field.tag)
    iter_step = len((list(uniq_fields)))  # шаг одного фио
    # шапка
    fields = [elem.tag for elem in all_roots[0:iter_step]]
    fields.append('ИсходныйФайл')
    ws.append(fields)
    # заполнение excel и словаря json
    start = 0  # индекс начала
    result_dict = dict()
    result_list = []
    try:
        for fio_num in range(int(len(all_roots) / iter_step)):
            line = []
            for elem in range(start, start + iter_step):
                line.append(all_roots[elem].text)
                # добавление имени файла в конец строки
                if len(line) == iter_step:
                    line.append(all_roots[elem].attrib['file'])
            start += iter_step  # увеличение индекса
            ws.append(line)  # запись в excel
            result_dict.update({key: value for key, value in zip(fields[:], line[:])})  # запись в словарь
            result_list.append(copy(result_dict))
    except Exception as e:
        print(e, ' xml to xlsx and json reformat problem!')
        return False
    # сохранение excel
    try:
        xlsx_save_file = os.path.join(xml_path, r'reformat\zup_fios_json_1C.xlsx')
        wb.save(xlsx_save_file)
    except Exception as e:
        print(e, ' xlsx save problem!')
        return False
    wb.close()
    try:
        xlsx_save_file = os.path.join(xml_path, r'reformat\zup_fios_json_1C.json')
        with open(xlsx_save_file, "w", encoding='utf-8') as file:
            json.dump(result_list, file, indent=2, ensure_ascii=False)
    except Exception as e:
        print(e, ' JSON save problem!')
        return False
    return result_dict


def xml_tabel_read(xml_file, xml_path):
    tree = element_tree.parse(xml_file)
    employee = dict()
    employees = []
    for elem in tree.findall('Общее'):
        for table in elem.findall('Таблица'):
            for key in table.keys():
                employee.update({key: table.get(key)})
            employees.append(copy(employee))
    save_file = os.path.join(xml_path, r'reformat\tabel_fios_json_1C.json')
    with open(save_file, 'w', encoding='utf-8') as json_file:
        json.dump(employees, json_file, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    path_tst = r'M:\Xranenie\Reportbolid'
    xml_to_xlsx(xml_path=path_tst)
    xml_tabel = 'ТабельЕРП(Новый).xml'
    xml_tabel_read(xml_tabel, path_tst)

