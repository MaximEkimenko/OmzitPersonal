import datetime
from pydantic import BaseModel
from database.database_crud_operations import get_all_divisions
from fastapi import APIRouter, Query, Body
from fastapi import FastAPI
from schemas import SEmployee, STimesheet

from schemas import Divisions
# from tst_in_personal import Divisions
from fastapi import Depends
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Employee, Timesheet
from typing import List, Annotated
from typing import Union

from database.database import async_session_factory, session_factory
from database.database import get_db, get_aync_db
from database.database import db_dependency

# аннотированная зависимость с БД
# db_dependency = Annotated[Session, Depends(get_db)]
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
    # TODO перенести логику БД в отдельный файл
    if not amount:
        query = select(Employee)
    else:
        query = select(Employee).where(Employee.id < amount)
    employees = await db.execute(query)
    res = [row[0] for row in employees.all()]
    return res


@router.get('/get_employee/{user_id}')
async def get_employee(user_id: int, db: async_db_dependency) -> List[SEmployee]:
    """
    Получение сотрудника по user_id
    :return:
    """
    # TODO перенести логику БД в отдельный файл
    query = select(Employee).where(Employee.id == user_id)
    employees = await db.execute(query)
    result = employees.scalars().all()
    result_schema = [SEmployee.model_validate(employee) for employee in result]
    return result_schema


@router.get('/timesheet')
async def get_timesheet(db: db_dependency, division: Divisions = None,
                        start_time: datetime.datetime = yesterday,
                        end_time: datetime.datetime = today) -> List[STimesheet]:
    """
    Получение табелей при не выбранном division возвращает всех работников
    :return:
    """
    if not division:
        query = ((select(Timesheet).where(Timesheet.date > start_time,
                                          Timesheet.date <= end_time,
                                          Timesheet.skud_day_duration != None
                                          ))
                 .select_from(Employee)
                 .join(Timesheet, Employee.id == Timesheet.employee_id))
    else:
        query = ((select(Timesheet).where(Timesheet.date > start_time,
                                          Timesheet.date <= end_time,
                                          Employee.division == division.value,
                                          Timesheet.skud_day_duration != None
                                          ))
                 .select_from(Employee)
                 .join(Timesheet, Employee.id == Timesheet.employee_id))
    timesheets = db.execute(query)
    result = timesheets.scalars().all()
    result_schema = [STimesheet.model_validate(timesheet) for timesheet in result]
    return result_schema


@router.get('/divisions')
def get_all_divisions(db: db_dependency):
    """
    Все подразделения компании из ЗУП
    :return:
    """
    query = select(Employee.division).distinct()
    result = db.execute(query)
    divisions = result.scalars().all()
    return divisions

# @router.get('/timesheet')
# async def get_timesheet(db: db_dependency, division: str = "Основное",
#                         start_time: datetime.datetime = '2024-05-01') -> List[STimesheet]:
#     """
#     Получение табелей
#     :return:
#     """
#     query = ((select(Timesheet).where(Timesheet.date > start_time,
#                                       Employee.division == division,
#                                       Timesheet.skud_day_duration != None
#                                       ))
#              .select_from(Employee)
#              .join(Timesheet, Employee.id == Timesheet.employee_id))
#     # query = select(Timesheet).where(Timesheet.id < 10).select_from(Employee).join(Timesheet, Employee.id == Timesheet.employee_id)
#     timesheets = db.execute(query)
#     result = timesheets.scalars().all()
#     result_schema = [STimesheet.model_validate(timesheet) for timesheet in result]
#     return result_schema


# @router.get('/async_timesheet')
# async def async_get_timesheet(db: async_db_dependency, division: str = "Основное",
#                               start_time: datetime.datetime = '2024-05-01') -> List[STimesheet]:
#     """
#     Получение табелей
#     :return:
#     """
#     query = ((select(Timesheet).where(Timesheet.date > start_time,
#                                       Employee.division == division,
#                                       Timesheet.skud_day_duration != None
#                                       ))
#              .select_from(Employee)
#              .join(Timesheet, Employee.id == Timesheet.employee_id))
#     # query = select(Timesheet).where(Timesheet.id < 10).select_from(Employee).join(Timesheet, Employee.id == Timesheet.employee_id)
#     timesheets = await db.execute(query)
#     result = timesheets.scalars().all()
#     print(result)
#     result_schema = [STimesheet.model_validate(timesheet) for timesheet in result]
#     print(result_schema)
#     return result_schema


# @router.post('/add_emp')
# async def add_employee(employee: Annotated[SEmployee, Depends()]):
#     """
#     Обновление данных
#     :param employee:
#     :return:
#     """
#     # test_emp.append(employee)
#     # print(test_emp)
#     return {'data': employee}
