def division_accumulation(division_1C: str) -> str | None:
    """
    Функция проверяет заполненное поле division в БД и сливает данные в один список
    если поле пустое
    :return:
    """
    simpled_div = division_1C.lower().strip()
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


def schedule_filler(division: str = None, schedule_1C: str = None) -> str | None:
    list_possible_2_2 = ('цех №1', 'цех №2', 'цех №3', 'цех №4', 'Участок малогабаритных конструкций')
    if division not in list_possible_2_2:
        return '5/2'
    else:
        return schedule_1C


if __name__ == '__main__':
    print(schedule_filler(division='fgdfg№1'))
    # tst_department_1C = 'ЦЕХ № 1'
    # print(division_accumulation(tst_department_1C))

