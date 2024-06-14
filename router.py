# TODO перенести логику БД в отдельный файл
import datetime
from fastapi import APIRouter
from schemas import SEmployee, STimesheet, SDivisions, TimeshitTODB, EmployeeToDB, JsonTo1C
from m_logger_settings import logger
from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Employee, Timesheet
from typing import List, Annotated, Dict

from database.database import get_db, get_aync_db
from database.database import db_dependency
from database.schedule_calculation import schedule_5_2
from service.python_to_1C import python_to_1C


async_db_dependency = Annotated[AsyncSession, Depends(get_aync_db)]

router = APIRouter(
    prefix="/e",
    tags=['main']
)

# сегодня
today = (datetime.datetime.now()).strftime("%Y-%m-%d")
# вчера
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")


@router.get('/get_all_employees')
async def get_all_employees(db: async_db_dependency, amount: int = None) -> List[SEmployee]:
    """
    Получение списка сотрудников.
    :amount: количество сотрудников. При незаполненном amount возвращает всех сотрудников.
    :return: None
    """

    if not amount:
        query = select(Employee)
    else:
        query = select(Employee).where(Employee.id < amount)
    employees = await db.execute(query)
    res = [row[0] for row in employees.all()]
    return res


@router.get('/get_employee/{user_id}')
async def get_employee(user_id: int, db: async_db_dependency) -> SEmployee:
    """
    Получение сотрудника по user_id
    :return:
    """
    # TODO перенести логику БД в отдельный файл
    query = select(Employee).where(Employee.id == user_id)
    employees = await db.execute(query)
    employee = employees.scalars().first()
    result_schema = SEmployee.model_validate(employee)
    return result_schema


@router.get('/timesheet')
async def get_timesheet(db: db_dependency, division: str = None,
                        start_time: datetime.datetime = yesterday,
                        end_time: datetime.datetime = today) -> List[STimesheet]:
    """
    Получение табелей при не выбранном division возвращает всех работников
    :return:
    """
    if not division:
        query = ((select(Timesheet).where(Timesheet.date >= start_time,
                                          Timesheet.date <= end_time,
                                          Timesheet.skud_day_duration != None
                                          # Employee.status == 'явка'
                                          ))
                 .select_from(Employee)
                 .join(Timesheet, Employee.id == Timesheet.employee_id))
    else:
        query = ((select(Timesheet).where(Timesheet.date >= start_time,
                                          Timesheet.date <= end_time,
                                          Employee.division == division,
                                          Timesheet.skud_day_duration != None
                                          # Employee.status == 'явка'
                                          ))
                 .select_from(Employee)
                 .join(Timesheet, Employee.id == Timesheet.employee_id))
    timesheets = db.execute(query)
    result = timesheets.scalars().all()
    result_schema = [STimesheet.model_validate(timesheet) for timesheet in result]
    return result_schema


@router.get('/divisions')
async def get_all_divisions(db: db_dependency) -> List[SDivisions]:
    """
    Все уникальные подразделения компании из ЗУП
    """
    allowed_list = ('цех №1', 'цех №2', 'цех №3', 'цех №4', 'Участок малогабаритных конструкций')
    query = (select(Employee.id, Employee.division).distinct(Employee.division)
             .where(Employee.division.in_(allowed_list)))
    result = db.execute(query).fetchall()
    return result


@router.post('/save')
async def save_timesheet(db: db_dependency, request: List[TimeshitTODB]):
    """
    Заполнение БД табелями
    :param db:
    :param request:
    :return:
    """
    status_dict = {'О': 'Отпуск', 'Б': 'Больничный', 'В': 'Выходной', 'К': 'Командировка',
                   'А': 'Административный отпуск'}

    for timesheet in request:
        for date, skud_value in timesheet.skud_day_duration.items():
            if skud_value == '':
                continue
            # подготовка данных
            # print(skud_value)
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            # fio = timesheet.employee.fio
            fio_id = timesheet.employee.id
            late_value = timesheet.late_value
            skud_night_duration = 0
            # print(late_value)
            if skud_value != '':
                if '|' in skud_value:
                    day_status = 'явка'
                    day_time, night_time = skud_value.split('|')
                    skud_day_duration = float(day_time[1:])
                    # print(f"{skud_day_duration=}")
                    skud_night_duration = float(night_time[1:])
                    # print(f"{skud_night_duration=}")
                    day_status_short = 'Я'
                    late_value = 0
                # буквенный статус
                elif skud_value in status_dict:
                    day_status = status_dict.get(skud_value)
                    day_status_short = skud_value
                    skud_day_duration = 0
                    late_value = 0
                # отсутствие
                elif skud_value == '0':
                    # print(skud_value)
                    day_status = 'Отсутствие'
                    skud_day_duration = 0
                    day_status_short = skud_value
                    late_value = 0
                # ночные / дневные
                else:
                    day_status = 'явка'
                    day_status_short = 'Я'
                    skud_day_duration = float(skud_value)
                # существующие записи
                exist_query = select(Timesheet).where(Timesheet.employee_id == fio_id,
                                                      Timesheet.date == date)
                existing_record = db.execute(exist_query).fetchone()



                if existing_record:
                    # проверка изменений
                    if all([existing_record[0].day_status == day_status,
                            existing_record[0].skud_day_duration == skud_day_duration,
                            existing_record[0].skud_day_duration == skud_night_duration,
                            existing_record[0].skud_day_duration == late_value,
                            ]):
                        continue
                    elif existing_record:
                        update_query = (update(Timesheet).where(Timesheet.employee_id == fio_id,
                                                                Timesheet.date == date)
                                        .values({'day_status': day_status,
                                                 'skud_day_duration': skud_day_duration,
                                                 'day_status_short': day_status_short,
                                                 'late_value': late_value,
                                                 'skud_night_duration': skud_night_duration}))
                        db.execute(update_query)
                        db.commit()
                else:
                    # добавление новой записи
                    new_record = Timesheet(employee_id=fio_id, date=date, day_status=day_status,
                                           skud_day_duration=skud_day_duration, day_status_short=day_status_short,
                                           late_value=late_value, skud_night_duration=skud_night_duration)
                    db.add(new_record)
                    db.commit()
    return 'ok'


@router.post('/save_employee')
async def save_employee(db: db_dependency, request: EmployeeToDB):
    """
       Функция сохранения списка сотрудников
       :param db:
       :param request:
       :return:
       """
    fio_id = request.id
    fio_division = request.division
    fio_schedule = request.schedule
    print(fio_id, fio_division, fio_schedule)
    update_query = update(Employee).where(Employee.id == fio_id).values({'division': fio_division,
                                                                         'schedule': fio_schedule})
    db.execute(update_query)
    db.commit()
    # запуск обновления данных при изменении графика на 5/2
    if fio_schedule == '5/2':
        schedule_5_2(fio_id)
    return {'status': 'ok'}


@router.get('/get1C')
async def get_1C_json(start_date: datetime.datetime,
                      end_date: datetime.datetime):
    result = python_to_1C(start_date=start_date, end_date=end_date, save_json=False)
    # print(result)
    return result

