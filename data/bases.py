import datetime
import sqlalchemy as sqla
from .db_session import SqlAlchemyBase


class Base(SqlAlchemyBase):
    __tablename__ = 'Bases'
    id = sqla.Column(sqla.Integer,
                           primary_key=True, autoincrement=True)
    # Ресурсы (0 = не продается)
    prices = sqla.Column(sqla.String(1000))
    # json в виде строки


