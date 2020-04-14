
from . import db_session 
import sqlalchemy
from sqlalchemy import *
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    from_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    whom_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    datetime = sqlalchemy.Column(sqlalchemy.Datetime, nullable=False)