import datetime

from fastapi import APIRouter
from fastapi import FastAPI
from schemas import SEmployee, STimesheet
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
    prefix="/emp",
    tags=['main']
)


#TODO TEST_ASYNC
@router.get('/async_all_emp')
async def async_get_employee_with_dependency(db: async_db_dependency) -> List[SEmployee]:
    """
    Получение сотрудников через get_db dependency
    :return:
    """
    query = select(Employee).where(Employee.id < 10)
    employees = await db.execute(query)
    # result = employees.scalars().all()
    # result_schema = [SEmployee.model_validate(employee) for employee in result]
    res = [row[0] for row in employees.all()]
    # return result_schema
    return res




# @router.get('')
# async def get_employees() -> List[SEmployee]:
#     """
#     Получение сотрудников через with и session_factory
#     :return:
#     """
#     async with async_session_factory() as session:
#         query = select(Employee).where(Employee.id < 10)
#         employees = await session.execute(query)
#         result = employees.scalars().all()
#         result_schema = [SEmployee.model_validate(employee) for employee in result]
#     return result_schema


@router.get('/all_emp')
async def get_employee_with_dependency(db: db_dependency) -> List[SEmployee]:
    """
    Получение сотрудников через get_db dependency
    :return:
    """
    query = select(Employee).where(Employee.id < 10)
    employees = db.execute(query)
    result = employees.scalars().all()
    result_schema = [SEmployee.model_validate(employee) for employee in result]
    return result_schema


@router.get('/one_emp/{user_id}')
async def get_one_employee_with_dependency(user_id: int, db: db_dependency) -> List[SEmployee]:
    """
    Получение сотрудника по user_id через get_db dependency
    :return:
    """
    query = select(Employee).where(Employee.id == user_id)
    employees = db.execute(query)
    result = employees.scalars().all()
    result_schema = [SEmployee.model_validate(employee) for employee in result]
    return result_schema


@router.get('/timesheet')
async def get_timesheet(start_time: datetime.datetime,
                        division: str,
                        db: db_dependency) -> List[STimesheet]:
    """
    Получение табелей
    :return:
    """
    query = ((select(Timesheet).where(Timesheet.date > start_time,
                                      Employee.division == division,
                                      Timesheet.skud_day_duration != None
                                      ))
             .select_from(Employee)
             .join(Timesheet, Employee.id == Timesheet.employee_id))
    # query = select(Timesheet).where(Timesheet.id < 10).select_from(Employee).join(Timesheet, Employee.id == Timesheet.employee_id)
    timesheets = db.execute(query)
    result = timesheets.scalars().all()
    result_schema = [STimesheet.model_validate(timesheet) for timesheet in result]
    return result_schema



@router.post('/add_emp')
async def add_employee(employee: Annotated[SEmployee, Depends()]):
    """
    Обновление данных
    :param employee:
    :return:
    """
    # test_emp.append(employee)
    # print(test_emp)
    return {'data': employee}
