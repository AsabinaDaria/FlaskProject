from . import db_session 
import sqlalchemy
from sqlalchemy import *
from .db_session import SqlAlchemyBase


class Users_pictures(SqlAlchemyBase):
    __tablename__ = 'users_pictures'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    file = sqlalchemy.Column(sqlalchemy.String, nullable=True)