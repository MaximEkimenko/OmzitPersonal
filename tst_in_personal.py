from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import registry, declarative_base, as_declarative

engine = create_engine("sqlite:///:memory:", echo=True)

@as_declarative()
class Abstract:
    pass

# Base = declarative_base()


class UserModel(Abstract):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(30))
    fullname = Column(String(30))



class AddressModel(Abstract):
    __tablename__ = 'addresses'
    id = Column(BigInteger, primary_key=True),
    user_id = Column(ForeignKey('users.id'))
    email = Column(String(30), nullable=False)


print(UserModel.__table__)
# print(AddressModel.__tablename__.__dict__)

# Base = declarative_base()

# metadata = MetaData()
#
# user_table = Table(
#     "users",
#     metadata,
#     Column("id", BigInteger, primary_key=True),
#     Column("user_id", BigInteger, unique=True),
#     Column("name", String(30)),
#     Column("fullname", String(30)),
#
# )
#
# addresses = Table(
#     "addresses",
#     metadata,
#     Column("id", BigInteger, primary_key=True),
#     Column("user_id", ForeignKey('users.user_id')),
#     Column("email", String(30), nullable=False),
#
# )
#
# metadata.create_all(bind=engine)
# metadata.drop_all(bind=engine)


# with engine.connect() as connection:
#     result = connection.execute(text("select 'hello world'"))
