from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from settings import BASEDIR
from settings import dotenv_path
from dotenv import load_dotenv
import os

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

HOST = os.getenv("ALCHEMY_DB_HOST")
NAME = os.getenv("ALCHEMY_DB_NAME")
USER = os.getenv("ALCHEMY_DB_USER")
PASSWORD = os.getenv("ALCHEMY_DB_PASSWORD")
PORT = os.getenv("ALCHEMY_DB_PORT")


database_url = f'postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

engine = create_engine(
    url=database_url,
    echo=False,
    max_overflow=10
)

session_factory = sessionmaker(engine)


class Base(DeclarativeBase):

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for index, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or index < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}\n")
        return f"<{self.__class__.__name__} {','.join(cols)}>"
