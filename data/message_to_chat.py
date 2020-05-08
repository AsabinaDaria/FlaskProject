from . import db_session 
import sqlalchemy
from sqlalchemy import *
from .db_session import SqlAlchemyBase


class Message_to_chat(SqlAlchemyBase):
    __tablename__ = 'message_to_chat'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    message = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    diection = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)