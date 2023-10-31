from datetime import datetime as dt
import datetime
from typing import Tuple, Optional

import pyodbc
from django.core.management import BaseCommand

from timesheet.models import Employee

POINTS = {
    'Турникет': (40, 41),
}

# данные для подключения к БД
BD_SERVER = '192.168.11.200'
BD_DATABASE = 'Orion15.11.2022'
BD_USERNAME = 'ASUP'
BD_PASSWORD = 'qC4HptD'


class Command(BaseCommand):
    help = "Выводит в консоль информацию со СКУД по сотрудникам из БД за последний день"

    def handle(self, *args, **options):
        get_timesheets(employers=tuple([employee.fio for employee in Employee.objects.all()]))


def get_night_shift_query(date, point, add_condition):
    night = (
        f"{date.strftime('%d.%m.%Y')} 12:00",
        f"{(date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')} 12:00"
    )
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
                            THEN SMALLDATETIMEFROMPARTS ( YEAR(pLogData.TimeVal), MONTH(pLogData.TimeVal), DAY(pLogData.TimeVal), 8, 00)
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
        GROUP BY t1.FIO, t1.HozOrgan
        HAVING DATEPART(day, MAX(t1.exit_time)) - DATEPART(day, MIN(t1.enter_time)) = 1;
        """, start, end
    return query


def get_day_shift_query(date, point, add_condition):
    day = (
        f"{date.strftime('%d.%m.%Y')}",
        f"{(date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')}"
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
                            THEN SMALLDATETIMEFROMPARTS ( YEAR(pLogData.TimeVal), MONTH(pLogData.TimeVal), DAY(pLogData.TimeVal), 8, 00)
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
        GROUP BY t1.FIO, t1.HozOrgan, DATEPART(day, t1.time);
        """, start, end
    return query


def get_timesheets(
        date: datetime = dt.date(dt.now() - datetime.timedelta(days=1)),
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

    # заполняем по списку сотрудников табель нулями
    if employers:
        result = {
            employee: (0, employee, None, None, None, 'Ошибка', 'Дневная')
            for employee in employers
        }
    else:
        result = {}

    errors_fios = []
    for query in queries:
        cursor.execute(*query)
        row = cursor.fetchone()
        while row:
            if row[1][5] == 'Ошибка':
                errors_fios.append(row[1][5])
            else:
                result[row[1]] = row
            row = cursor.fetchone()
    cnxn.close()

    # если выбрана проверка всех сотрудников, то в ошибки добавляем отметившихся, но отсутствующих на данной точке доступа
    if not employers:
        for fio in get_all_fios(date):
            if fio[1] not in result and fio[0] != 2:
                data = (None, fio[1], fio[0], None, None, 'Ошибка', 'Дневная')
                print(data)
                errors_fios.append(data)

    return result


def get_all_fios(date: datetime = dt.date(dt.now() - datetime.timedelta(days=1))):
    day = (
        f"{date.strftime('%d.%m.%Y')}",
        f"{(date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')}"
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
    get_timesheets(employers=tuple([employee.fio for employee in Employee.objects.all()]))
