from fastapi import FastAPI
from schemas import SEmployee, STimesheet
from fastapi import Depends
from typing import Annotated
from router import router

app = FastAPI()
app.include_router(router)



@app.get('/')
async def get_home():
    return {"data": "started"}


