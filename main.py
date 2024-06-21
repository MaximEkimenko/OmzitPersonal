from fastapi import FastAPI
from router import router
from fastapi.middleware.cors import CORSMiddleware

description = """ 
1. get_all_employees
   - Получение списка всех сотрудников из БД.
   - Параметры:
     - amount (необязательно): ограничение количества возвращаемых сотрудников.
   - Возвращает: список объектов SEmployee.
2. get_employee(user_id: int, db: AsyncSession) -> SEmployee:
   - Получение данных одного сотрудника по его идентификатору.
   - Параметры:
     - user_id: идентификатор сотрудника.
   - Возвращает: объект SEmployee.
3. get_timesheet
   - Получение табелей учета рабочего времени.
   - Параметры:
     - division (необязательно): подразделение для фильтрации.
     - start_time (необязательно): начальная дата для фильтрации.
     - end_time (необязательно): конечная дата для фильтрации.
   - Возвращает: список объектов STimesheet.
4. get_all_divisions
   - Получение списка всех уникальных подразделений из БД.
   - Возвращает: список объектов SDivisions.
5. save_timesheet
   - Сохранение табелей учета рабочего времени в БД.
   - Параметры:
     - request: список объектов TimeshitTODB с данными для сохранения.
   - Возвращает: строку "ok" в случае успешного сохранения.
6. save_employee
   - Сохранение данных одного сотрудника в БД.
   - Параметры:
     - request: объект EmployeeToDB с данными для сохранения.
   - Возвращает: словарь с ключом "status" и значением "ok" в случае успешного сохранения.
7. get_1C_json
   - Получение данных для 1С (переведенные поля) в формате JSON.
   - Параметры:
     - start_date: начальная дата для фильтрации.
     - end_date: конечная дата для фильтрации.
   - Возвращает: объект JsonTo1C с данными для 1С.
"""

app = FastAPI(title='Формирование табелей', description=description, version="0.0.1",)
app.include_router(router)


@app.get('/')
async def get_home():
    return {"data": "started"}


origins = [
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8888',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:7000',
    'http://localhost:3000',
    'http://localhost:8080',
    'http://0.0.0.0:8080',
    'http://0.0.0.0:8888',
    'http://0.0.0.0:7001',
    'http://0.0.0.0:5001',
    'http://0.0.0.0:5000',
    'http://0.0.0.0:8004',
    'http://0.0.0.0:8005',
    'http://0.0.0.0:3000',
    'http://192.168.8.163:3000',
    'http://192.168.8.163:7001/'
    'http://192.168.8.163:7000/'
    'http://192.168.8.163:8004/'
    'http://192.168.8.163:8005/'
    'http://192.168.8.163:5001/'

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
