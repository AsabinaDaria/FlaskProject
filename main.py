from data import db_session
from flask import *
from data.db_session import SqlAlchemyBase
from data.users import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

def main():
    db_session.global_init("db/ff.sqlite")
    user = User()
    user.name = "Ridley"
    user.surname = "Ridley"
    user.login = "scott_chief@mars.org"
    user.sex = '12345678'
    user.file = '12345678'
    user.password = '12345678'
    user.remember_me = True
    user.about = '12345678'
    session = db_session.create_session()
    query = session.query(User)
    f = (User.name == "Ridley")
    for user in query.filter(f):
        print(user.login)
    session.add(user)
    session.commit()
    app.run()


if __name__ == '__main__':
    main()
