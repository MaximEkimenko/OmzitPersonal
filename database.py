from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

HOST = '127.0.0.1'
NAME = 'personal'
USER = 'admin'
PASSWORD = 'Epass1'
PORT = 5432

database_url = f'postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

engine = create_engine(
    url=database_url,
    # echo=True,
    max_overflow=10
)

session_factory = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
