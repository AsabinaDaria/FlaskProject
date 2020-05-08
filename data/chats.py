from . import db_session 
import sqlalchemy
from sqlalchemy import *
from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    from_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    whom_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)