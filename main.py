from fastapi import FastAPI
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
