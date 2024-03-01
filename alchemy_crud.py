import datetime

from database import session_factory
from models_alchemy import Employee, Timesheet
from sqlalchemy import select


def add_line():
    with session_factory() as session:
        line = Employee(fio='Name Surname Fatherhood',
                        employment_date=datetime.datetime.now(), fired_date=datetime.datetime.now())
        session.add(line)
        session.commit()


def select_line():
    with session_factory() as session:
        query = select(Employee)
        result = session.execute(query)
        workers = result.scalars().all()[0].fio

        print(f"{workers=}")
        # for line in result.all():
        #     print(line[0].values)


def update_line():
    line_id = 4
    with session_factory() as session:
        worker = session.get(Employee, line_id)
        worker.fio = "NEW_FIO"
        session.commit()


if __name__ == '__main__':
    # select_line()
    add_line()
    # update_line()
