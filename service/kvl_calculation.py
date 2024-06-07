import calendar
import datetime
import math


def kvl_calculation(employment_date: datetime) -> tuple[float, float]:
    """
    Функция расчитывает коэффициент выслуги лет по утверждённой методике на сегодняшний день
    на первый день прошлого месяца
    :param employment_date: дата принятия на работу
    :return: kvl_today, kvl_last_month
    """
    def kvl_diff(work_time):
        """Вспомогательная функция для вычисления коэффициента выслуги лет"""
        if work_time > 2:
            kvl = math.floor(work_time) / 100 if work_time < 10 else 0.1
        else:
            kvl = 0
        return kvl
    employment_date = datetime.datetime.strptime(employment_date, '%Y-%m-%dT00:00:00')  # дата из строки
    today = datetime.datetime.now()  # сегодняшняя дата
    after_last_month = datetime.datetime.now() - datetime.timedelta(days=60)  # позапрошлый месяц
    # последний день предыдущего месяца
    _, last_day = calendar.monthrange(after_last_month.year, after_last_month.month)
    last_month_date = datetime.datetime(year=after_last_month.year, month=after_last_month.month, day=last_day)
    work_time_now = (today - employment_date).days / 365  # лет работы на сегодня
    work_time_last_month = (last_month_date - employment_date).days / 365  # лет работы на сегодня
    kvl_today = kvl_diff(work_time_now)  # kvl на сегодня
    kvl_last_month = kvl_diff(work_time_last_month)  # kvl на начало предыдущего месяца
    return kvl_today, kvl_last_month


if __name__ == '__main__':
    tst_date = '2012-06-01T00:00:00'
    print(kvl_calculation(tst_date))
