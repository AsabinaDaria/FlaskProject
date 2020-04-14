from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask import *
from flask_bootstrap import Bootstrap
from main import *
from data import db_session
from flask import *
from data.db_session import SqlAlchemyBase
from data.users import *
#from flask_login import *
import requests
import os
from flask_wtf.file import *
from werkzeug.utils import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
Bootstrap(app)
#login = LoginManager(app)


class LoginForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    about = TextAreaField('Статус', validators=None)
    file = FileField(validators=None)
    #file = FileField(validators=[FileRequired()])
    sex = SelectField('Укажите Ваш пол:', choices=[('1', 'женский'), ('2', 'мужской')], validators=None)
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Регистрация')


class HomeForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
# username=form.login.data[:form.login.data.find('@')]),
# print(url_for('account', user_id=user_id,  username=username)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = HomeForm()
    if form.validate_on_submit():
        db_session.global_init("db/ff.sqlite")
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            if session.query(User).filter(User.password == form.password.data).first():
                user_me = session.query(User).filter_by(login=form.login.data).first()
                user_id = user_me.id
                return redirect(url_for('account', user_id=user_id))
            else:
                return render_template('home.html', title='Вход', form=form, message="Неверно указан пароль")
        else:
            return render_template('home.html', title='Вход', form=form, message="Неверно указан логин")
        user_me = session.query(User).filter_by(login=form.login.data).first()
        user_id = user_me.id
        return redirect(url_for('account', user_id=user_id))
    return render_template('home.html', title='Вход', form=form)


@app.route('/register', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_session.global_init("db/ff.sqlite")
        if form.password.data != form.password_again.data:
            print(9)
            return render_template('login.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            print(7)
            return render_template('login.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        print(999)
        
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.login = form.login.data
        user.password = form.password.data
        user.about = form.about.data
        # user.file = filename
        user.sex = form.sex.data
        user.remember_me = form.remember_me.data
        session = db_session.create_session()
        session.add(user)
        session.commit()
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)
        photo = str(user.id) + str(file_extension[1])
        file.save(os.path.join('C:/Users/я/Desktop/new_project/static/img', photo))
        user.file = photo
        session.commit()
        return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/account/<int:user_id>', methods=['GET', 'POST'])
def account(user_id):
    db_session.global_init("db/ff.sqlite")
    session = db_session.create_session()
    user_me = session.query(User).filter(User.id == user_id).first()
    user_pict = user_me.file
    name = user_me.name
    surname = user_me.surname
    about = user_me.about
    sex = user_me.sex
    filename = str('img/' + str(user_id) + '.jpg')
    return render_template('profile.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex)



#@app.route('/account/<id>', methods=['GET', 'POST'])
#def l():
#    form = LoginForm()
#    db_session.global_init("db/ff.sqlite")
#    session = db_session.create_session()
#    for user in session.query(User).all():
#        print(user.password)
#    return render_template('login.html', title='Авторизация', form=form)



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')