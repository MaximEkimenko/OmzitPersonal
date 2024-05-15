import xml.etree.ElementTree as element_tree
import json
from copy import copy
import pandas as pd
import os
from m_logger_settings import logger


def xml_accumulate(xml_path: str) -> list:
    """
    Функция возвращает список всех элементов из всех xml файлов в директории xml_path
    :param xml_path:
    :return: list
    """
    file_list = []
    for root_dir, path_dirs, path_files in os.walk(xml_path):
        for file in path_files:
            # if '.xml' in file and '~' not in file:
            if '.xml' in file:
                if xml_path == root_dir:
                    file_list.append(file)
    logger.debug(f'список xml файлов {file_list} в директории {xml_path}.')
    all_roots = []
    for file in file_list:
        file_path = os.path.join(xml_path, file)
        tree = element_tree.parse(file_path)
        root_xmls = tree.getroot()
        for xml_element in root_xmls:
            xml_element.set('file', file)  # добавление имени файла в элемент
            all_roots.append(xml_element)
    if not all_roots:
        logger.error(f'ОТСУТСВУЮ ФАЙЛЫ XML в ДИРЕКТОРИИ {xml_path}')
    return all_roots


def xml_zup_read(xml_path: str, xlsx_file: str, json_file: str) -> list or False:
    """
    Функция прообразует все файлы xml из директории xml_path в xlsx и json
    :param xml_path: путь к исходной директории xml
    :param json_file:  путь к результирующему json файлу
    :param xlsx_file: путь к результирующему xlsx
    :return: список
    """
    # получение списка всех xml
    try:
        all_roots = xml_accumulate(xml_path)
        # logger.debug(f'содержимое xml файлов {all_roots=}')
        logger.info(f"Все xml в {xml_path} удачно прочитаны.")
    except Exception as e:
        logger.error(f"Ошибка чтения xml файлов в директории {xml_path}.")
        logger.exception(e)
        return False
    # количество полей
    uniq_fields = set()
    for uniq_field in all_roots:
        uniq_fields.add(uniq_field.tag)
    iter_step = len((list(uniq_fields)))  # шаг одного фио
    # шапка
    fields = [elem.tag for elem in all_roots[0:iter_step]]
    fields.append('ИсходныйФайл')  # дополнительное поле имени исходного файла
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
            result_dict.update({key: value for key, value in zip(fields[:], line[:])})  # запись в словарь
            result_list.append(copy(result_dict))
        logger.info("Переформатирование xml в xlsx и json прошло успешно.")
    except Exception as e:
        logger.error(f'Ошибка переформатирования xml в xlsx и json')
        logger.exception(e)
        return False
    #  сохранение в excel
    # xlsx_save_file = os.path.join(xml_path, xlsx_file)
    try:
        df = pd.DataFrame(result_list)
        df.to_excel(xlsx_file, index=False)
        logger.info(f"Сохранение EXCEL файла {xlsx_file} прошло успешно.")
    except Exception as e:
        logger.error(f"Ошибка сохранения Excel файла {xlsx_file}.")
        logger.exception(e)
        return False
    #  сохранение в json
    # json_save_file = os.path.join(xml_path, json_file)
    try:
        with open(json_file, "w", encoding='utf-8') as file:
            json.dump(result_list, file, indent=2, ensure_ascii=False)
        logger.info(f"Сохранение JSON файла {json_file} прошло успешно.")
    except Exception as e:
        logger.error(f"Ошибка сохранения JSON файла {json_file}")
        logger.exception(e)
        return False
    return result_list


def xml_tabel_read(xml_file: str, json_file: str) -> list:
    """
    Функция создает JSON файл из xml файла табеля
    :param xml_file: имя исходного xml файла
    :param json_file: имя результирующего json файла
    :return: список
    """
    tree = element_tree.parse(xml_file)
    employee = dict()
    employees = []
    for elem in tree.findall('Общее'):
        for table in elem.findall('Таблица'):
            for key in table.keys():
                employee.update({key: table.get(key)})
            employees.append(copy(employee))
    # save_file = os.path.join(xml_path, json_file)
    try:
        with open(json_file, 'w', encoding='utf-8') as j_file:
            json.dump(employees, j_file, indent=2, ensure_ascii=False)
        logger.info(f"Файл {json_file} сохранён успешно.")
    except Exception as e:
        logger.error(f"Ошибка сохранения {json_file}.")
        logger.exception(e)
    return employees


if __name__ == '__main__':
    path_tst = r'M:\Xranenie\Reportbolid\new_tst'
    xlsx_tst = r'M:\Xranenie\Reportbolid\reformat\zup_fios_json_1C.xlsx'
    json_tst = r'M:\Xranenie\Reportbolid\reformat\zup_fios_json_1C.json'
    json_tabel_tst = r'reformat\tabel_fios_json_1C.json'
    xml_zup_read(xml_path=path_tst, xlsx_file=xlsx_tst, json_file=json_tst)


    # xml_tabel = 'ТабельЕРП(Новый).xml'
    # xml_tabel_read(xml_file=xml_tabel, xml_path=path_tst, json_file=json_tabel_tst)

