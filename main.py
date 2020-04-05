from data.db_session import *
from data import db_session 
from flask import *
import sqlalchemy
from data.db_session import SqlAlchemyBase
from data.users import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

def main():
    pass


if __name__ == '__main__':
    main()
