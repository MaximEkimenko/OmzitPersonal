from fastapi import FastAPI
from schemas import SEmployee, STimesheet
from fastapi import Depends
from typing import Annotated
app = FastAPI()


@app.get('/')
async def get_home():
    return {"data": "started"}


@app.get('/emp')
async def get_employee():
    emp = SEmployee(fio='Иванов Иван Иванович')
    return {"data": emp}


@app.get('/timesheet')
async def get_timesheet():
    return {"data": "started"}


test_emp = []


@app.post('/add_emp')
async def add_employee(employee: Annotated[SEmployee, Depends()]):
    test_emp.append(employee)
    print(test_emp)
    return {'data': employee}

