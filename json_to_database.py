from models_alchemy import Employee, Timesheet
import json


class DataInsert:
    """
    класс записи и обновления данных в БД
    """
    def __init__(self,  json_file: str):
        """
        :param json_file: json файл с данными для записи вы БД
        """
        self.json_file = json_file
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





if __name__ == '__main__':
    a = DataInsert(r'D:\АСУП\Python\Projects\OmzitPersonal\json\fio_full_json.json')

