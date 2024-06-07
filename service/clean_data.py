import datetime
import shutil
from pprint import pprint
import json, os
from m_logger_settings import logger
from constants import BASEDIR
from service.kvl_calculation import kvl_calculation
from service.division_accunulation import division_accumulation
from constants import MODE
from dotenv import load_dotenv


if MODE == 'test':
    from constants import test_dotenv_path as dotenv_path
if MODE == 'docker':
    from constants import dotenv_path as dotenv_path
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def clean_data(json_data: list) -> list:
    """
    Функция очистки json_data от мусорных данных
    :param json_data:
    :return:
    """
    # onec_dir_json = r'/personal_app/xml_data/reformat'  # директория хранения json docker
    # onec_dir_json = r'D:\xml_data\reformat'  # тесты
    onec_dir_json = os.getenv("ONEC_DIR_JSON")
    today = datetime.datetime.now()
    clean_zup_fio_list = []  # результирующий список
    uniq_fios = set()  # множество уникальных фио
    for line in json_data:
        add_to_clean_data = False  # переменная для передачи недавно уволенных
        if line['fio'] not in uniq_fios:
            keys = []  # даты документов
            part_keys = []  # даты документов совместителей
            # словарь по датам
            one_fio_dict = {d['document_date'][:-8]: d for d in json_data if d['fio'] == line['fio']}
            for key in one_fio_dict:
                # if one_fio_dict[key].get('division', None) is None:
                #     one_fio_dict[key].update({'division': 'Не определено'})
                # Добавление КВЛ
                kvl_today, kvl_last_month = kvl_calculation(one_fio_dict[key]['employment_date'])
                one_fio_dict[key].update({'KVL': kvl_today, 'KVL_last_month': kvl_last_month})
                # объединение мусорных подразделений (только для новых записей)
                true_division = division_accumulation(one_fio_dict[key]['fio'],
                                                      one_fio_dict[key]['division_1C'])
                if true_division:
                    one_fio_dict[key].update({'division': true_division})
                else:
                    one_fio_dict[key].update({'division': one_fio_dict[key]['division_1C']})
                # определение самого позднего документа по ФИО с фильтровкой совместительства
                date = datetime.datetime.strptime(key, '%d.%m.%Y')
                if one_fio_dict[key]['job_type'] == 'Основное место работы':
                    keys.append(date)
                else:
                    part_keys.append(date)
            # обработка совместителей если только совместитель, то отметка в должности
            if not keys and part_keys:
                last_date_part_str = datetime.datetime.strftime(sorted(part_keys)[-1], '%d.%m.%Y')
                one_fio_dict[last_date_part_str]['job_title'] += ' ТОЛЬКО СОВМЕСТИТЕЛЬ'
                if (one_fio_dict[last_date_part_str]['document'] != 'Увольнение' and
                        'я.' not in one_fio_dict[last_date_part_str]['company_name']):
                    logger.info(f"Определено только совместительство для {one_fio_dict[last_date_part_str]['fio']}")
                keys = part_keys  # добавление только совместителей в формирование результирующего список
            # дата последнего документа по ФИО
            last_date = sorted(keys)[-1]
            # дата последнего документа по ФИО строка
            last_date_str = datetime.datetime.strftime(sorted(keys)[-1], '%d.%m.%Y')
            # простановка статусов отпусков, больничных согласно statuses.py
            # отпуск
            if (today - last_date < datetime.timedelta(days=14) and
                    today >= last_date and
                    'Отпуск' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'ОТ'
                logger.info(f"Активный отпуск {one_fio_dict[last_date_str]['fio']}")
            # больничный
            elif (today - last_date < datetime.timedelta(days=1) and
                  today >= last_date and
                  'Отсутствие (болезнь, прогул, неявка)' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'Б'
                logger.info(f"Активный больничный {one_fio_dict[last_date_str]['fio']}")
            # командировка
            elif (today - last_date < datetime.timedelta(days=1) and
                  today >= last_date and
                  'Активная командировка' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'К'
                logger.info(f"Командировка {one_fio_dict[last_date_str]['fio']}")
            # Административный отпуск
            elif (today - last_date < datetime.timedelta(days=1) and
                  today >= last_date and
                  'Отпуск без сохранения оплаты' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'ДО'
                logger.info(f"Отпуск без сохранения оплаты {one_fio_dict[last_date_str]['fio']}")
            # удалённая работа
            elif (today - last_date < datetime.timedelta(days=1) and
                  today >= last_date and
                  'Отсутствие с сохранением оплаты' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'УДАЛЁНКА'
                logger.info(f"Отсутствие с сохранением оплаты {one_fio_dict[last_date_str]['fio']}")
            elif (today - last_date < datetime.timedelta(days=14) and
                  today >= last_date and
                  'Увольнение' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = f'Уволен {last_date_str}'
                add_to_clean_data = True
                logger.info(f"Уволен {last_date_str}:  {one_fio_dict[last_date_str]['fio']}")
            else:
                one_fio_dict[last_date_str]['status'] = 'явка'
            # фильтровка уволенных и мусорных данных
            if ((one_fio_dict[last_date_str]['document'] != 'Увольнение' or add_to_clean_data) and
                    'я.' not in one_fio_dict[last_date_str]['company_name']):
                clean_zup_fio_list.append(one_fio_dict[last_date_str])
            uniq_fios.add(line['fio'])  # добавление пройденных ФИО в множество для следующей итерации
    # сохранение и копирование чистого json
    clean_zup_fio_list_json_file = BASEDIR / 'json' / 'clean_zup_fios_to_python.json'
    try:
        with open(clean_zup_fio_list_json_file, 'w', encoding='utf-8') as j_file:
            json.dump(clean_zup_fio_list, j_file, indent=2, ensure_ascii=False)
            logger.info(f"Полный файл JSON {clean_zup_fio_list_json_file} сохранён и скопирован в общий успешно.")
        shutil.copy(clean_zup_fio_list_json_file, onec_dir_json)
    except Exception as e:
        logger.error(f"Ошибка сохранения или копирования {clean_zup_fio_list_json_file}.")
        logger.exception(e)
    # print(len(clean_zup_fio_list))
    return clean_zup_fio_list


if __name__ == '__main__':
    json_file = r'D:\xml_data\reformat\zup_fios_json_python.json'
    with open(json_file, 'r', encoding='utf-8') as json_f:
        new_zup_fios_list = json.load(json_f)
    clean_data(new_zup_fios_list)
