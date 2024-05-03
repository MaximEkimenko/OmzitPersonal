from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import Optional
from typing import List, Dict
from database.models import Timesheet, Employee


class SEmployee(BaseModel):
    """
    Сотрудник
    """
    id: int | None = None
    employment_date: datetime | None = None
    fired_date: datetime | None = None
    birthday_date: datetime | None = None
    fio: str
    job_title: str | None = None
    rank_title: str | None = None
    tabel_number: str | None = None
    tabel_filename: str | None = None
    tariff_rate: str | None = None
    division: str | None = None
    status: str | None = None
    schedule: str | None = None
    shift_hours: str | None = None
    skud_access: str | None = None
    day_start: str | None = None
    boss: str | None = None
    KTR_category: str | None = None
    KTR: str | None = None
    has_NAX: str | None = None
    KNAX: str | None = None
    # данные для 1С
    fio_responsible: str | None = None
    INN_employee: str | None = None
    INN_responsible: str | None = None
    INN_company: str | None = None
    # timesheets: dict | None = None

    class Config:
        from_attributes = True


class STimesheet(BaseModel):
    """
    Табель сотрудника
    """
    id: int | None = None
    date: datetime | None = None
    # фио сотрудник

    # employee_id: int
    employee: SEmployee
    day_status: str | None = None
    # Поля СКУД
    skud_day_start_1: datetime | None = None
    skud_day_end_1: datetime | None = None
    skud_day_duration: int | None = None
    skud_night_duration: int | None = None
    is_day_alter: bool | None = None
    altered_day_duration: int | None = None
    altered_night_duration: int | None = None
    is_night_alter: bool | None = None
    skud_error: bool | None = None
    skud_error_query: str | None = None

    class Config:
        from_attributes = True


# class STimesheetDisplay(STimesheet):
#     id: int | None = None
#     date: datetime | None = None
#     # фио сотрудник
#     employee: SEmployee
#     # employee_id: int
#     day_status: str | None = None
#     # Поля СКУД
#     skud_day_start_1: datetime | None = None
#     skud_day_end_1: datetime | None = None
#     skud_day_duration: int | None = None
#     skud_night_duration: int | None = None
#     is_day_alter: bool | None = None
#     altered_day_duration: int | None = None
#     altered_night_duration: int | None = None
#     is_night_alter: bool | None = None
#     skud_error: bool | None = None
#     skud_error_query: str | None = None
#
#     class Config:
#         from_attributes = True
#

class SEmployeeDisplay(SEmployee):
    fio: str | None = None
    division: str | None = None

    class Config:
        from_attributes = True

