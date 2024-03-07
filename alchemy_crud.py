import datetime

from database import session_factory
from models_alchemy import Employee, Timesheet
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload


def add_line():
    with session_factory() as session:
        line = Timesheet(date=datetime.datetime.now(), employee_id=1)
        # line = Employee(fio='another fio',
        #                 employment_date=datetime.datetime.now(), fired_date=datetime.datetime.now(),
        #                 job_title='title_2',
        #                 tariff_rate=300,
        #                 schedule=11)
        session.add(line)
        session.commit()



def select_line():
    with session_factory() as session:
        # query = select(Employee)
        # result = session.execute(query)
        # workers = result.scalars().all()[0].fio
        # print(f"{workers=}")
        # query2 = select(Timesheet).options(joinedload(Timesheet.employee))
        query2 = select(Timesheet).options(selectinload(Timesheet.employee))
        result = session.execute(query2)
        # employees1 = result.scalars().all().employee.fio
        for el in result.scalars().all():
            print(el)
        # employees2 = result.scalars().all().employee.fio
        # print(f"{employees1=}")




def update_line():
    line_id = 4
    with session_factory() as session:
        worker = session.get(Employee, line_id)
        worker.fio = "NEW_FIO"
        session.commit()





if __name__ == '__main__':
    select_line()
    # add_line()
    # update_line()
