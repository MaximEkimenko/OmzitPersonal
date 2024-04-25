import datetime
from pprint import pprint
import json
from m_logger_settings import logger
from settings import BASEDIR


def clean_data(json_data: list) -> list:
    today = datetime.datetime.now()
    clean_zup_fio_list = []
    uniq_fios = set()  # множество уникальных фио
    for line in json_data:
        if line['fio'] not in uniq_fios:
            keys = []
            # словарь по датам
            one_fio_dict = {d['document_date'][:-8]: d for d in json_data if d['fio'] == line['fio']}
            # определение самого позднего документа по ФИО
            for key in one_fio_dict:
                date = datetime.datetime.strptime(key, '%d.%m.%Y')
                keys.append(date)
            # дата последнего документа по ФИО
            last_date = sorted(keys)[-1]
            # дата последнего документа по ФИО строка
            last_date_str = datetime.datetime.strftime(sorted(keys)[-1], '%d.%m.%Y')
            # простановка статусов отпусков, больничных согласно statuses.py
            if (today - last_date < datetime.timedelta(days=14) and
                    today >= last_date and
                    'Отпуск' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'ОТ'
                logger.info(f"Активный отпуск {one_fio_dict[last_date_str]['fio']}")
            elif (today - last_date < datetime.timedelta(days=1) and
                  today >= last_date and
                  'Отсутствие(болезнь, прогул, неявка)' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'Б'
                logger.info(f"Активный больничный {one_fio_dict[last_date_str]['fio']}")
            elif (today - last_date < datetime.timedelta(days=1) and
                  today >= last_date and
                  'Активная командировка' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'К'
                logger.info(f"Командировка {one_fio_dict[last_date_str]['fio']}")
            elif (today - last_date < datetime.timedelta(days=1) and
                  today >= last_date and
                  'Отпуск без сохранения оплаты' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'ДО'
                logger.info(f"Отпуск без сохранения оплаты {one_fio_dict[last_date_str]['fio']}")
            elif (today - last_date < datetime.timedelta(days=1) and
                  today >= last_date and
                  'Отсутствие с сохранением оплаты' == one_fio_dict[last_date_str]['document']):
                one_fio_dict[last_date_str]['status'] = 'УДАЛЁНКА'
                logger.info(f"Отсутствие с сохранением оплаты {one_fio_dict[last_date_str]['fio']}")
            else:
                one_fio_dict[last_date_str]['status'] = 'явка'

            # обработка уволенных и мусорных данных
            if (one_fio_dict[last_date_str]['document'] != 'Увольнение' and
                    'я.' not in one_fio_dict[last_date_str]['company_name']):
                # clean_fio_dict = {line['fio']: one_fio_dict[last_date_str]}
                # clean_fio_dict = {line['fio']: one_fio_dict[last_date_str]}
                clean_zup_fio_list.append(one_fio_dict[last_date_str])
                # TODO обработать совместительство
                # if 'совместительство' in one_fio_dict[last_date_str]['job_type']:
                #     print(line)
            uniq_fios.add(line['fio'])  # добавление пройденных ФИО в множество

    # сохранение чистого json
    clean_zup_fio_list_json_file = str(BASEDIR / 'json' / 'clean_zup_fios_to_python.json')

    try:
        with open(clean_zup_fio_list_json_file, 'w', encoding='utf-8') as j_file:
            json.dump(clean_zup_fio_list_json_file, j_file, indent=2, ensure_ascii=False)
            logger.info(f"Полный файл JSON {clean_zup_fio_list_json_file} сохранён успешно.")
    except Exception as e:
        logger.error(f"Ошибка сохранения {clean_zup_fio_list_json_file}.")
        logger.exception(e)

    # pprint(clean_zup_fio_list)
    print(len(clean_zup_fio_list))

    return clean_zup_fio_list


if __name__ == '__main__':
    json_file = r'M:\Xranenie\Reportbolid\reformat\zup_fios_json_python.json'
    with open(json_file, 'r', encoding='utf-8') as json_f:
        new_zup_fios_list = json.load(json_f)

    clean_data(new_zup_fios_list)
