from fastapi import APIRouter
from fastapi import FastAPI
from schemas import SEmployee, STimesheet, STimesheetDisplay, SEmployeeDisplay
from fastapi import Depends
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models_alchemy import Employee, Timesheet
from typing import List, Annotated
from typing import Union

from database.database import async_session_factory, session_factory
from database.database import get_db

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/emp",
    tags=['main']
)


@router.get('')
async def get_employee() -> List[SEmployee]:
    """
    Получение сотрудников через with и session_factory
    :return:
    """
    async with async_session_factory() as session:
        query = select(Employee).where(Employee.id < 10)
        employees = await session.execute(query)
        result = employees.scalars().all()
        result_schema = [SEmployee.model_validate(employee) for employee in result]
    return result_schema


@router.get('tsts')
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


async def tst():
    async with async_session_factory() as session:
        query = select(Timesheet).where(Timesheet.employee_id == 1)
        timesheets = await session.execute(query)
        result = timesheets.scalars().all()

@router.get('/timesheet')
async def get_timesheet() -> List[STimesheet]:
    """
    Получение табелей
    :return:
    """
    async with async_session_factory() as session:
        query = select(Timesheet).where(Timesheet.employee_id == 1)
        timesheets = await session.execute(query)
        result = timesheets.scalars().all()
        result_schema = [STimesheet.model_validate(timesheet) for timesheet in result]
    return result_schema


@router.get('/full_timesheet', response_model=STimesheetDisplay)
async def get_timesheet() -> List[STimesheet]:
    """
    Получение табелей
    :return:
    """

    async with async_session_factory() as session:
        query = select(Timesheet).where(Timesheet.employee_id == 1)
        timesheets = await session.execute(query)
        result = timesheets.scalars().all()
        result_schema = [STimesheet.model_validate(timesheet) for timesheet in result]
    return result_schema






test_emp = []


@router.post('/add_emp')
async def add_employee(employee: Annotated[SEmployee, Depends()]):
    """
    Обновление данных
    :param employee:
    :return:
    """
    test_emp.append(employee)
    print(test_emp)
    return {'data': employee}
