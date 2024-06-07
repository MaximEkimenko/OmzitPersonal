from database.database_crud_operations import get_division


def division_accumulation(fio: str, division_1C: str) -> str | None:
    """
    Функция проверяет заполненное поле division в БД и сливает данные в один список
    если поле пустое
    :return:
    """
    simpled_div = division_1C.lower().strip()
    is_division = get_division(fio)
    # print(is_division)
    # true_dvision = division_1C
    if not is_division:  # Если запись ещё нет
        if 'цех' in simpled_div:  # обработка только цеховых
            if '1' in simpled_div:
                true_dvision = 'цех №1'
            elif '2' in simpled_div:
                true_dvision = 'цех №2'
            elif '3' in simpled_div:
                true_dvision = 'цех №3'
            elif '4' in simpled_div:
                true_dvision = 'цех №4'
            else:
                true_dvision = 'Неизвестный цех'
            return true_dvision

        else:
            return division_1C
    else:
        return None


if __name__ == '__main__':
    pass

    # divs = get_all_divisions()
    # pprint(divs)
    tst_department_1C = 'ЦЕХ № 1'
    print(division_accumulation('Вольных Вячеслав Юрьевич', tst_department_1C))
    # for div in divs:
    #     division_accumulation('Вольных Вячеслав Юрьевич', div)
