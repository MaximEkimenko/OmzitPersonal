

def convert_list_to_dict(data):
    """
    Преобразование списка в словарь
    :param data:
    :return:
    """
    dict_from_list = {}
    field_value = 'Сотрудник'
    for item in data:
        fio = item['Сотрудник']
        if fio in dict_from_list:
            for key, value in item.items():
                if key != field_value:
                    if key not in dict_from_list[fio]:
                        dict_from_list[fio][key] = str(value)
        else:
            dict_from_list[fio] = {}
            for key, value in item.items():
                if key != field_value:
                    dict_from_list[fio][key] = str(value)

    return dict_from_list


def convert_list_to_dict_with_filter(data, filter_list):
    """
    Преобразование списка в словарь с учётом фильтрации данных
    :param filter_list: Список фильтрации
    :param data:
    :return:
    """
    dict_from_list = {}
    field_value = 'Сотрудник'
    for index, item in enumerate(data):
        fio = item['Сотрудник']
        filter_field = item['Ответственный']
        if filter_field in filter_list:
            if fio in dict_from_list:
                for key, value in item.items():
                    if key != field_value:
                        if key not in dict_from_list[fio]:
                            dict_from_list[fio][key] = str(value)
            else:
                dict_from_list[fio] = {}
                for key, value in item.items():
                    if key != field_value:
                    # if key != field_value and filter_field in filter_list:
                        dict_from_list[fio][key] = str(value)
        else:
            pass
            # print('!!!!!!!!!!!!!!', dict_from_list.get(fio), fio)
            # del data[index]
    return dict_from_list


if __name__ == '__main__':
    pass
