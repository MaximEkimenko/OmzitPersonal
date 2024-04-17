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
