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
    # данные для 1С
    fio_responsible: Mapped[Optional[str]]  # фио отвественного
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
    day_status: Mapped[Optional[str]] = mapped_column(String(10))  # статус работы в день (больничный, отпуск etc)
    # Поля СКУД
    skud_day_start_1: Mapped[date_type]   # вход день
    skud_day_end_1: Mapped[date_type]  # выход день
    skud_day_duration: Mapped[Optional[int]] = mapped_column(SmallInteger)  # длительность дня
    skud_night_duration: Mapped[Optional[int]] = mapped_column(SmallInteger)  # длительность ночи
    is_day_alter: Mapped[Optional[bool]] = mapped_column(Boolean)  # факт изменения табеля дня
    altered_day_duration: Mapped[Optional[int]] = mapped_column(SmallInteger)  # корректированная длительность дня
    altered_night_duration: Mapped[Optional[int]] = mapped_column(SmallInteger)  # корректированная длительность ночи
    is_night_alter: Mapped[Optional[bool]] = mapped_column(Boolean)  # факт изменения табеля ночи
    skud_error: Mapped[Optional[bool]] = mapped_column(Boolean)  # факт ошибки скуд
    skud_error_query: Mapped[Optional[str]] = mapped_column(String)






if __name__ == '__main__':
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
#     pass
