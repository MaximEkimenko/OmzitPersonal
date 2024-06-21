import datetime
from typing import Optional, Annotated
from sqlalchemy import MetaData, DateTime, Integer, String, SmallInteger, BigInteger, Boolean, Float, ForeignKey
try:
    from database.database import Base
except ModuleNotFoundError:
    from database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
try:
    from database.database import engine
except Exception:
    from database import engine


intpk = Annotated[int, mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)]
date_type = Annotated[datetime.datetime, mapped_column(DateTime, nullable=True)]


class Employee(Base):
    """
    Модель сотрудника
    """
    __tablename__ = 'employee_test'
    id: Mapped[intpk]
    employment_date: Mapped[Optional[date_type]]  # Дата принятия на работу
    fired_date: Mapped[Optional[date_type]]  # дата увольнения
    birthday_date: Mapped[Optional[date_type]]  # дата рождения
    fio: Mapped[str] = mapped_column(String)  # ФИО
    job_title: Mapped[Optional[str]] = mapped_column(String(255))  # должность
    rank_title: Mapped[Optional[str]] = mapped_column(SmallInteger)  # разряд
    tabel_number: Mapped[Optional[str]] = mapped_column(String(30))  # табельный номер
    tabel_filename: Mapped[Optional[str]] = mapped_column(String(255))  # имя файла табеля 1С
    tariff_rate: Mapped[Optional[str]] = mapped_column(Integer)  # тарифная ставка
    division: Mapped[Optional[str]] = mapped_column(String(255))  # подразделение
    status: Mapped[str] = mapped_column(String(255), nullable=True)  # статус ?
    schedule: Mapped[Optional[str]] = mapped_column(String(255))  # график работы
    shift_hours: Mapped[Optional[str]] = mapped_column(SmallInteger)  # часов в смене
    skud_access: Mapped[Optional[str]] = mapped_column(SmallInteger)  # точка доступа скуд
    day_start: Mapped[Optional[str]] = mapped_column(SmallInteger)  # время начала рабочей смены
    boss: Mapped[Optional[str]] = mapped_column(String(255))  # руководитель
    KTR_category: Mapped[Optional[str]] = mapped_column(String(50))  # категория КТР
    KTR: Mapped[Optional[float]] = mapped_column(Float)  # значение КТР
    has_NAX: Mapped[Optional[bool]] = mapped_column(Boolean)  # есть НАКС
    KNAX: Mapped[Optional[float]] = mapped_column(Float)  # значение коэффициента НАКС
    KVL: Mapped[Optional[float]] = mapped_column(Float)  # значение коэффициента выслуги лет
    KVL_last_month: Mapped[Optional[float]] = mapped_column(Float)  # значение КВЛ за прошлый месяц
    division_1C: Mapped[Optional[str]] = mapped_column(String(255))  # подразделение в 1С
    schedule_1C: Mapped[Optional[str]] = mapped_column(String(255))  # график работы

    # данные для 1С
    fio_responsible: Mapped[Optional[str]]  # фио ответственного
    INN_employee:  Mapped[Optional[str]] = mapped_column(String(50))  # ИНН сотрудника
    INN_responsible: Mapped[Optional[str]] = mapped_column(String(50))  # ИНН ответственного
    INN_company: Mapped[Optional[str]] = mapped_column(String(50))  # ИНН юр.лица
    timesheets: Mapped["Timesheet"] = relationship("Timesheet", back_populates="employee")
    # timesheets = relationship("Timesheet", back_populates="employee")


class Timesheet(Base):
    """ Модель табеля сотрудника """
    __tablename__ = 'timesheet_test'
    id: Mapped[intpk]
    date: Mapped[date_type]  # дата работы сотрудника
    # фио сотрудник
    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employee_test.id", ondelete='CASCADE'))
    employee: Mapped["Employee"] = relationship("Employee", back_populates='timesheets')
    # employee = relationship(Employee, back_populates='timesheets')
    day_status: Mapped[Optional[str]] = mapped_column(String(200))  # статус работы (больничный, отпуск etc)
    day_status_short: Mapped[Optional[str]] = mapped_column(String(10))  # статус работы коротко
    # Поля СКУД
    skud_day_start_1: Mapped[date_type]   # вход день
    skud_day_end_1: Mapped[date_type]  # выход день
    skud_day_duration: Mapped[Optional[float]] = mapped_column(Float)  # длительность дня
    skud_night_duration: Mapped[Optional[float]] = mapped_column(Float)  # длительность ночи
    is_day_alter: Mapped[Optional[bool]] = mapped_column(Boolean)  # факт изменения табеля дня
    altered_day_duration: Mapped[Optional[int]] = mapped_column(SmallInteger)  # корректированная длительность дня
    altered_night_duration: Mapped[Optional[int]] = mapped_column(SmallInteger)  # корректированная длительность ночи
    is_night_alter: Mapped[Optional[bool]] = mapped_column(Boolean)  # факт изменения табеля ночи
    skud_error: Mapped[Optional[bool]] = mapped_column(Boolean)  # факт ошибки скуд
    skud_error_query: Mapped[Optional[str]] = mapped_column(String)
    late_value: Mapped[Optional[float]] = mapped_column(Float)


class CalendarDays(Base):
    """Модель дней """
    __tablename__ = 'calendar_days'
    id: Mapped[intpk]
    date: Mapped[date_type]   # дата
    day_type: Mapped[str] = mapped_column(String)  # тип дня (выходной, рабочий, сокращённый)


class Responsible(Base):
    """ Модель ответственных """
    __tablename__ = 'responsible'
    id: Mapped[intpk]
    fio: Mapped[Optional[str]] = mapped_column(String)  # фио ответственного


# class Latecomers(Base):
#     """Модель опоздунов """
#     __tablename__ = 'latecomers'
#     id: Mapped[intpk]
#     date: Mapped[date_type]  # дата
#     employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employee_test.id", ondelete='CASCADE'))
#     employee: Mapped["Employee"] = relationship("Employee", back_populates='timesheets')



if __name__ == '__main__':
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
#     pass
