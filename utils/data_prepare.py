import datetime
import json
from copy import copy


class DataPrepare:
    """
    класс подготовки данных 1C в json в БД
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
        Перевод полей 1С json в поля БД
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
