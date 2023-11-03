import datetime

from typing import Tuple, Optional, Dict

import pyodbc
from django.core.management import BaseCommand
from django.db import IntegrityError

from timesheet.models import Employee, Timesheet

POINTS = {
    'Турникет': (40, 41),
}

ONE_DAY = datetime.timedelta(days=1)

# данные для подключения к БД
BD_SERVER = '192.168.11.200'
BD_DATABASE = 'Orion15.11.2022'
BD_USERNAME = 'ASUP'
BD_PASSWORD = 'qC4HptD'


class Command(BaseCommand):
    help = "Выводит в консоль информацию со СКУД по сотрудникам из БД за последний день"

    def handle(self, *args, **options):
        def create_or_update_timesheet(data: Dict):
            data['fio'] = Employee.objects.get(fio=employee)
            try:
                existing_timesheet = Timesheet.objects.get(fio=data['fio'], date=data['date'])
                if existing_timesheet.skud_day_start_1 or existing_timesheet.skud_day_end_1:
                    existing_timesheet.skud_day_start_2 = data['skud_day_start_1']
                    existing_timesheet.skud_day_end_2 = data['skud_day_end_1']
                else:
                    existing_timesheet.skud_day_start_1 = data['skud_day_start_1']
                    existing_timesheet.skud_day_end_1 = data['skud_day_end_1']

                if existing_timesheet.skud_night_start_1 or existing_timesheet.skud_night_end_1:
                    existing_timesheet.skud_night_start_2 = data['skud_night_start_1']
                    existing_timesheet.skud_night_end_2 = data['skud_night_end_1']
                else:
                    existing_timesheet.skud_night_start_1 = data['skud_night_start_1']
                    existing_timesheet.skud_night_end_1 = data['skud_night_end_1']

                if not existing_timesheet.skud_day_duration and data['skud_day_duration']:
                    existing_timesheet.skud_day_duration = data['skud_day_duration']
                elif existing_timesheet.skud_day_duration and data['skud_day_duration']:
                    existing_timesheet.skud_day_duration += data['skud_day_duration']
                else:
                    pass

                if not existing_timesheet.skud_night_duration and data['skud_night_duration']:
                    existing_timesheet.skud_night_duration = data['skud_night_duration']
                elif existing_timesheet.skud_night_duration and data['skud_night_duration']:
                    existing_timesheet.skud_night_duration += data['skud_night_duration']
                else:
                    pass
                existing_timesheet.save()
            except Timesheet.DoesNotExist:
                try:
                    Timesheet.objects.create(**data)
                except IntegrityError:
                    raise IntegrityError(f'{data}')

        employees = tuple([employee.fio for employee in Employee.objects.all()])
        # интервал выгрузки
        date = datetime.date(day=1, month=11, year=2023)
        date_end = datetime.date(day=30, month=11, year=2023)
        # date = date_end = datetime.datetime.today() - ONE_DAY
        while date <= date_end:
            timesheets = get_timesheets(employers=employees, date=date)
            for employee, data in timesheets.items():
                if isinstance(data, list):
                    for i_data in data:
                        i_data['fio'] = Employee.objects.get(fio=employee)
                        create_or_update_timesheet(data=i_data)
                else:
                    create_or_update_timesheet(data=data)
            date += ONE_DAY


def get_night_shift_query(date, point, add_condition):
    night = (
        f"{date.strftime('%d.%m.%Y')} 12:00",
        f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 12:00"
    )
    next_day = f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 00:00"
    end_night_shift = f"{(date + ONE_DAY).strftime('%d.%m.%Y')} 05:00"

    start, end = night
    query = f"""
        SELECT 
            ROUND((DATEDIFF(minute, MIN(t1.enter_time), MAX(t1.exit_time)))/60, 0, 1) as work_time, 
            t1.FIO, 
            t1.HozOrgan, 
            MIN(t1.enter_time), 
            MAX(t1.exit_time),
            CASE
                WHEN MIN(t1.enter_time) >= MAX(t1.exit_time) OR MIN(t1.enter_time) is Null OR MAX(t1.exit_time) is Null
                    THEN 'Ошибка'
                ELSE 'ОК'
            END AS Correct,
            'Ночная'
        FROM
            (SELECT
                t2.HozOrgan,
                pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName AS FIO,
                t2.Mode,
                CASE 
                    WHEN t2.Mode = 1
                        THEN t2.TimeVal
                    ELSE Null
                END AS enter_time,
                CASE 
                    WHEN t2.Mode = 2
                        THEN t2.TimeVal
                    ELSE Null
                END AS exit_time,
                t2.TimeVal
            FROM pLogData AS t2
            JOIN pList ON t2.HozOrgan = pList.ID
            WHERE (t2.TimeVal >= ?
            AND t2.TimeVal < ?
            {add_condition}
            AND t2.Event in (13, 29, 32)
            AND t2.DoorIndex in {point})
            ) AS t1
        GROUP BY t1.FIO, t1.HozOrgan
        HAVING (DATEDIFF(day, MIN(t1.enter_time), MAX(t1.exit_time)) = 1) 
                OR (MIN(t1.enter_time) >= ? AND MIN(t1.enter_time) <= ?);
        """, start, end, next_day, end_night_shift
    return query


def get_day_shift_query(date, point, add_condition):
    day = (
        f"{date.strftime('%d.%m.%Y')} 06:00",
        f"{(date + ONE_DAY).strftime('%d.%m.%Y')}"
    )
    start, end = day
    query = f"""
        SELECT
            ROUND((DATEDIFF(minute, MIN(t1.enter_time), MAX(t1.exit_time)) - 60)/60, 0, 1) as work_time,
            t1.FIO,
            t1.HozOrgan,
            MIN(t1.enter_time),
            MAX(t1.exit_time),
            CASE
                WHEN MIN(t1.enter_time) >= MAX(t1.exit_time) OR MIN(t1.enter_time) is Null OR MAX(t1.exit_time) is Null
                    THEN 'Ошибка'
                ELSE 'ОК'
            END AS Correct,
            'Дневная'
        FROM
            (SELECT
                t2.HozOrgan,
                pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName AS FIO,
                t2.Mode,
                CASE
                WHEN t2.Mode = 1
                THEN t2.time
                ELSE Null
                END AS enter_time,
                CASE
                WHEN t2.Mode = 2
                THEN t2.time
                ELSE Null
                END AS exit_time,
                t2.time
            FROM
                (SELECT
                    CASE
                        WHEN DATEPART(hour, pLogData.TimeVal) < 8 AND pLogData.Mode = 1
                            THEN SMALLDATETIMEFROMPARTS (
                                    YEAR(pLogData.TimeVal), 
                                    MONTH(pLogData.TimeVal), 
                                    DAY(pLogData.TimeVal), 
                                    8, 00
                                    )
                        ELSE pLogData.TimeVal
                        END AS time, *
                 FROM pLogData
                ) AS t2
            JOIN pList ON t2.HozOrgan = pList.ID
            WHERE (t2.TimeVal >= ?
            AND t2.TimeVal < ?
            {add_condition}
            AND t2.Event in (13, 29, 32)
            AND t2.DoorIndex in {point})
            ) AS t1
        GROUP BY t1.FIO, t1.HozOrgan, DATEPART(day, t1.time)
        HAVING MAX(t1.exit_time) > SMALLDATETIMEFROMPARTS (
                                            YEAR(MAX(t1.exit_time)), 
                                            MONTH(MAX(t1.exit_time)), 
                                            DAY(MAX(t1.exit_time)), 
                                            8, 00);
        """, start, end
    return query


def get_timesheets(
        date: datetime = datetime.datetime.date(datetime.datetime.now() - ONE_DAY),
        employers: Optional[Tuple] = None,
        point: str = 'Турникет'
):
    cnxn = pyodbc.connect(
        f'DRIVER=SQL Server;'
        f'SERVER={BD_SERVER};'
        f'DATABASE={BD_DATABASE};'
        f'UID={BD_USERNAME};'
        f'PWD={BD_PASSWORD}',
    )
    cursor = cnxn.cursor()

    # добавляем условие по выбранным сотрудникам
    if employers and len(employers) == 1:
        employers = (employers[0], '')
        add_condition = f"AND pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName in {employers}"
    elif employers and len(employers) > 1:
        add_condition = f"AND pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName in {employers}"
    else:
        add_condition = ''

    queries = [
        get_day_shift_query(date, POINTS[point], add_condition),
        get_night_shift_query(date, POINTS[point], add_condition)
    ]

    # Добавляем всех выбранных сотрудников в словарь с нулевыми значениями
    if employers:
        result = {
            employee: {
                    'date': date,
                    'skud_day_start_1': None,
                    'skud_day_end_1': None,
                    'skud_day_duration': None,
                    'skud_night_start_1': None,
                    'skud_night_end_1': None,
                    'skud_night_duration': None,
                }
            for employee in employers
        }
    else:
        result = {}

    errors_fios = []

    # Обновляем словарь с сотрудниками данными из БД СКУД
    for query in queries:
        cursor.execute(*query)
        row = cursor.fetchone()
        while row:
            if row[5] == 'Ошибка':
                errors_fios.append(row[1])

            if row[6] == 'Дневная':
                print('Дневная')
                result[row[1].strip()] = {
                    'date': date,
                    'skud_day_start_1': row[3],
                    'skud_day_end_1': row[4],
                    'skud_day_duration': row[0],
                    'skud_night_start_1': None,
                    'skud_night_end_1': None,
                    'skud_night_duration': None,
                }

            # TODO Добавить обработку ситуаций если пришел с 22 до 00 или с 00 до 6
            elif row[6] == 'Ночная':
                def count_hours(start, end):
                    return int((end - start).total_seconds() / 3600)

                end_current_date = datetime.datetime.combine(
                    date=date,
                    time=datetime.time(23, 59, 59)
                )

                next_day = datetime.datetime.combine(
                    date=date + ONE_DAY,
                    time=datetime.time(00, 00, 00)
                )

                end_day_shift = datetime.datetime.combine(
                    date=date,
                    time=datetime.time(22, 00, 00)
                )
                end_night_shift = datetime.datetime.combine(
                    date=date + ONE_DAY,
                    time=datetime.time(6, 00, 00)
                )
                # с 18 до 7
                if row[3] < end_day_shift and row[4] > end_night_shift:
                    print('Ночная с 18 до 7')
                    result[row[1].strip()] = [
                        {
                            'date': date,
                            'skud_day_start_1': row[3],
                            'skud_day_end_1': end_day_shift,
                            'skud_day_duration': count_hours(start=row[3], end=end_day_shift),
                            'skud_night_start_1': end_day_shift,
                            'skud_night_end_1': end_current_date,
                            'skud_night_duration': count_hours(start=end_day_shift, end=next_day),
                        },
                        {
                            'date': next_day,
                            'skud_day_start_1': end_night_shift,
                            'skud_day_end_1': row[4],
                            'skud_day_duration': count_hours(start=end_night_shift, end=row[4]),
                            'skud_night_start_1': next_day,
                            'skud_night_end_1': end_night_shift,
                            'skud_night_duration': count_hours(start=next_day, end=end_night_shift) - 1,
                        }
                    ]
                # с 18 до 6
                elif row[3] < end_day_shift and row[4] <= end_night_shift:
                    print('Ночная с 18 до 6')
                    result[row[1].strip()] = [
                        {
                            'date': date,
                            'skud_day_start_1': row[3],
                            'skud_day_end_1': end_day_shift,
                            'skud_day_duration': count_hours(start=row[3], end=end_day_shift),
                            'skud_night_start_1': end_day_shift,
                            'skud_night_end_1': end_current_date,
                            'skud_night_duration': count_hours(start=end_day_shift, end=next_day),
                        },
                        {
                            'date': next_day,
                            'skud_day_start_1': None,
                            'skud_day_end_1': None,
                            'skud_day_duration': None,
                            'skud_night_start_1': next_day,
                            'skud_night_end_1': end_night_shift,
                            'skud_night_duration': count_hours(start=next_day, end=end_night_shift) - 1 if count_hours(
                                start=next_day, end=end_night_shift) > 0 else 0,
                        }
                    ]
                # с 22 до 7
                elif end_day_shift <= row[3] <= end_current_date and row[4] > end_night_shift:
                    print('Ночная с 22 до 7')
                    result[row[1].strip()] = [
                        {
                            'date': date,
                            'skud_day_start_1': None,
                            'skud_day_end_1': None,
                            'skud_day_duration': None,
                            'skud_night_start_1': end_day_shift,
                            'skud_night_end_1': end_current_date,
                            'skud_night_duration': count_hours(start=end_day_shift, end=next_day),
                        },
                        {
                            'date': next_day,
                            'skud_day_start_1': end_night_shift,
                            'skud_day_end_1': row[4],
                            'skud_day_duration': count_hours(start=end_night_shift, end=row[4]),
                            'skud_night_start_1': next_day,
                            'skud_night_end_1': end_night_shift,
                            'skud_night_duration': count_hours(start=next_day, end=end_night_shift) - 1,
                        }
                    ]
                # с 22 до 6
                elif end_day_shift <= row[3] <= end_current_date and row[4] <= end_night_shift:
                    print('Ночная с 22 до 6')
                    result[row[1].strip()] = [
                        {
                            'date': date,
                            'skud_day_start_1': None,
                            'skud_day_end_1': None,
                            'skud_day_duration': None,
                            'skud_night_start_1': end_day_shift,
                            'skud_night_end_1': end_current_date,
                            'skud_night_duration': count_hours(start=end_day_shift, end=next_day),
                        },
                        {
                            'date': next_day,
                            'skud_day_start_1': None,
                            'skud_day_end_1': None,
                            'skud_day_duration': None,
                            'skud_night_start_1': next_day,
                            'skud_night_end_1': end_night_shift,
                            'skud_night_duration': count_hours(start=next_day, end=end_night_shift) - 1,
                        }
                    ]
                # с 00 до 7
                elif row[3] >= next_day and row[4] > end_night_shift:
                    print('Ночная с 00 до 7')
                    result[row[1].strip()] = {
                        'date': next_day,
                        'skud_day_start_1': end_night_shift,
                        'skud_day_end_1': row[4],
                        'skud_day_duration': count_hours(start=end_night_shift, end=row[4]),
                        'skud_night_start_1': next_day,
                        'skud_night_end_1': end_night_shift,
                        'skud_night_duration': count_hours(start=next_day, end=end_night_shift) - 1,
                    }
                # с 00 до 6
                elif row[3] >= next_day and row[4] <= end_night_shift:
                    print('Ночная с 00 до 6')
                    result[row[1].strip()] = {
                        'date': next_day,
                        'skud_day_start_1': None,
                        'skud_day_end_1': None,
                        'skud_day_duration': None,
                        'skud_night_start_1': next_day,
                        'skud_night_end_1': end_night_shift,
                        'skud_night_duration': count_hours(start=next_day, end=end_night_shift) - 1 if count_hours(
                            start=next_day, end=end_night_shift) > 0 else 0,
                    }
                else:
                    raise Exception(f'Неучтенный период работы с {row[3]} до {row[4]}')
            else:
                print(f'Неизвестный статус смены: {row[6]}')
            print(date, row)
            row = cursor.fetchone()
    cnxn.close()
    # если выбрана проверка всех сотрудников, то в ошибки добавляем отметившихся,
    # но отсутствующих на данной точке доступа
    if not employers:
        for fio in get_all_fios(date):
            if fio[1] not in result and fio[0] != 2:
                data = (None, fio[1], fio[0], None, None, 'Ошибка', 'Дневная')
                errors_fios.append(data)
    return result


def get_all_fios(date: datetime = datetime.datetime.date(datetime.datetime.now() - ONE_DAY)):
    day = (
        f"{date.strftime('%d.%m.%Y')}",
        f"{(date + ONE_DAY).strftime('%d.%m.%Y')}"
    )
    start, end = day
    cnxn = pyodbc.connect(
        f'DRIVER=SQL Server;'
        f'SERVER={BD_SERVER};'
        f'DATABASE={BD_DATABASE};'
        f'UID={BD_USERNAME};'
        f'PWD={BD_PASSWORD}',
    )
    cursor = cnxn.cursor()

    query = f"""
            SELECT
                DISTINCT (pLogData.HozOrgan),
                pList.Name + ' ' + pList.FirstName + ' ' + pList.MidName AS FIO
            FROM pLogData
            JOIN pList ON pLogData.HozOrgan = pList.ID
            WHERE pLogData.TimeVal >= ?
            AND pLogData.TimeVal < ?
        """, start, end
    result = []
    cursor.execute(*query)
    row = cursor.fetchone()
    while row:
        result.append((row[0], row[1]))
        row = cursor.fetchone()
    cnxn.close()
    return result


if __name__ == "__main__":
    get_timesheets()
