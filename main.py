from fastapi import FastAPI
from schemas import SEmployee, STimesheet
from fastapi import Depends
from typing import Annotated
from router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='personal_timesheets')
app.include_router(router)



@app.get('/')
async def get_home():
    return {"data": "started"}


origins = [
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8888',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)