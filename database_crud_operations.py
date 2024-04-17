import datetime
from database import session_factory
from models_alchemy import Employee, Timesheet
from sqlalchemy import select, insert, update
from sqlalchemy.orm import joinedload, selectinload
import json



def add_line(json_file):

    with open(json_file, 'r', encoding='utf8') as file:
        json_data = json.load(file)
    # SELECT строки по фио и статусу Работа !ПРЕДВАРИТЕЛЬНО ОБЕСПЕЧИВ УНИКАЛЬНОСТЬ!
    # Если строка exists и не изменилась, то update
    # иначе insert

    with session_factory() as session:
        session.execute(insert(Employee), json_data)
        session.commit()

        # line = Timesheet(date=datetime.datetime.now(), employee_id=1)
        # line = Employee(fio='another fio',
        #                 employment_date=datetime.datetime.now(), fired_date=datetime.datetime.now(),
        #                 job_title='title_2',
        #                 tariff_rate=300,
        #                 schedule=11)
        # session.add(line)
        # session.commit()


def select_line():
    with session_factory() as session:
        query = select(Employee)
        # result = session.execute(query)
        # workers = result.scalars().all()[0].fio
        # print(f"{workers=}")
        # query2 = select(Timesheet).options(joinedload(Timesheet.employee))
        query2 = select(Timesheet)
        result = session.execute(query)
        # employees1 = result.scalars().all().employee.fio
        for line in result.scalars().all():
            print(line)
            # for el in line:
            #     print(el)
            # print(line)
        # employees2 = result.scalars().all().employee.fio
        # print(f"{employees1=}")




def update_line():
    line_id = 4
    with session_factory() as session:
        worker = session.get(Employee, line_id)
        worker.fio = "NEW_FIO"
        session.commit()





if __name__ == '__main__':
    json_file_tst = r'D:\АСУП\Python\Projects\OmzitPersonal\json\fio_full_json.json'
    add_line(json_file_tst)
    # update_line()
    # select_line()
