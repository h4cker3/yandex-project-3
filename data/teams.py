import datetime
import sqlalchemy as sqla
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import LoginManager, UserMixin, login_user, logout_user


class Team(SqlAlchemyBase, UserMixin):
    __tablename__ = 'Teams'
    id = sqla.Column(sqla.Integer,
                           primary_key=True, autoincrement=True)
    name = sqla.Column(sqla.String(300), nullable=True, unique=True)
    username = sqla.Column(sqla.String(300), unique=True)
    password = sqla.Column(sqla.String(300))
    penalty = sqla.Column(sqla.Integer, nullable=True)
    orgtype = sqla.Column(sqla.String(300), default="player")
    base_id = sqla.Column(sqla.Integer, nullable=True)
    code = sqla.Column(sqla.String(20), index=True, unique=True)
    # Ресурсы
    res = sqla.Column(sqla.String(1000))

