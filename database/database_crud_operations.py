try:
    from database.database import session_factory, async_session_factory
except Exception:
    from database import session_factory, async_session_factory
try:
    from database.models import Employee, Timesheet
except Exception:
    from models import Employee, Timesheet

from sqlalchemy import select, insert, update
from m_logger_settings import logger


def bulk_add(data: list) -> None:
    """
    Функция добавляет в БД данные из словаря dict по ФИО.
    :param data:
    :return:
    """
    for line in data:
        # запрос проверка существования ФИО в БД
        stmt = select(Employee.fio).where(Employee.fio == line['fio']).exists()
        with session_factory() as session:
            # проверка существования ФИО в БД
            is_line_exist = session.execute(select(stmt)).scalars().first()
            if not is_line_exist:
                # если нет добавление в БД
                session.execute(insert(Employee), line)
                session.commit()
                logger.debug(f"Добавлено {line}.")
            else:
                logger.debug(f"Уже существует в БД {line}.")


def bulk_update(data: list) -> None:
    """
    Функция обновляет данные в БД сз словаря data.
    :param data:
    :return:
    """
    # SELECT строки по фио и статусу в которой другой статус
    for line in data:
        # запрос
        stmt = select(Employee.id).where(Employee.status != line['status'],
                                         Employee.fio == line['fio'])
        with session_factory() as session:
            is_line_exist = session.execute(select(stmt.exists())).scalars().first()
            if is_line_exist:
                # id строки
                line_id = session.execute(stmt).scalars().first()
                # обновление значения
                session.execute(update(Employee).where(Employee.id == line_id),
                                {'status': line['status']})
                session.commit()
                logger.debug(f"Обновлено {line}")
            else:
                logger.debug(f"{line} - Статус не изменился. Не обновлено")


def get_all_data():
    """
    NOT USED
    :param data:
    :return:
    """
    with session_factory() as session:
        # employee_dict = data.model_dump()
        data = session.execute(select(Employee)).scalars().all()
    return data


def get_all_divisions():
    """
    Функция возвращает все подразделения компании
    :return:
    """
    with session_factory() as session:
        result = session.execute(select(Employee.division).distinct())
        divisions = result.scalars().all()
    return tuple(divisions)


def select_line():
    """
    NOT USABLE
    :return:
    """
    with session_factory() as session:
        query = select(Employee)
        query2 = select(Timesheet)
        result = session.execute(query)
        for line in result.scalars().all():
            print(line)


def update_line():
    """
    NOT USABLE
    :return:
    """
    line_id = 4
    with session_factory() as session:
        worker = session.get(Employee, line_id)
        worker.fio = "NEW_FIO"
        session.commit()


if __name__ == '__main__':
    print(get_all_divisions())
    pass

