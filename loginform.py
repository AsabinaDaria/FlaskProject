from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask import *
from flask_bootstrap import Bootstrap
from main import *
from data import db_session
from flask import *
from data.db_session import *
from data import db_session 
from data.users import *
from data.users_pictures import *
from data.message_to_chat import *
#from flask_login import *
import requests
import os
from flask_wtf.file import *
from werkzeug.utils import *
import hashlib
import binascii
import os
from sqlalchemy.orm import sessionmaker
from main import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
Bootstrap(app)


class LoginForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField(
        'Повторите пароль', validators=[DataRequired()])
    about = TextAreaField('Статус', validators=None)
    file = FileField(validators=None)
    #file = FileField(validators=[FileRequired()])
    sex = SelectField('Укажите Ваш пол:', choices=[
                      ('1', 'женский'), ('2', 'мужской')], validators=None)
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Регистрация')


class HomeForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class MailForm(FlaskForm):
    directionform = StringField('кому', validators=[DataRequired()])
    submit = SubmitField('Войти')


class MailFormChat(FlaskForm):
    messageform = PasswordField('сообщение', validators=[DataRequired()])
    submit = SubmitField('Войти')


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


@app.route('/', methods=['GET', 'POST'])
def index():
    form = HomeForm()
    if form.validate_on_submit():
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        user_data = DBsession.query(User).filter(
            User.login == form.login.data).first()
        if user_data:
            password = user_data.password
            if verify_password(password, form.password.data) == True:
                user_me = DBsession.query(User).filter_by(
                    login=form.login.data).first()
                user_id = user_me.id
                session['logged_in'] = user_data.id
                return redirect(url_for('account_page', user_id=user_id))
            else:
                return render_template('home.html', title='Вход', form=form, message="Неверно указан пароль")
        else:
            return render_template('home.html', title='Вход', form=form, message="Неверно указан логин")
        user_me = DBsession.query(User).filter_by(
            login=form.login.data).first()
        user_id = user_me.id
        session['logged_in'] = str(user_data.id)
        return redirect(url_for('account_page', user_id=user_id))
    return render_template('home.html', title='Вход', form=form)


def check_user(user_id):
    if 'logged_in' in session:
        if user_id == session.get('logged_in'):
            return True
        return False
    return False


@app.route('/register', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        global db_session
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        if form.password.data != form.password_again.data:
            print(9)
            return render_template('login.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        DBsession = db_session.create_session()
        if DBsession.query(User).filter(User.login == form.login.data).first():
            return render_template('login.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.login = form.login.data
        user.password = hash_password(form.password.data)
        user.about = form.about.data
        user.sex = form.sex.data
        user.remember_me = form.remember_me.data
        DBsession = db_session.create_session()
        DBsession.add(user)
        DBsession.commit()
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)
        photo = str(user.id) + str(file_extension[1])
        file.save(os.path.join(
            "C:/Users/я/Downloads/project_with_chats/project/static/img/", photo))
        user.file = photo
        DBsession.commit()
        return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/account/<int:user_id>/acc_page', methods=['GET', 'POST'])
def account_page(user_id):
    if check_user(user_id):
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        user_me = DBsession.query(User).filter(User.id == user_id).first()
        users_files = [url_for('static', filename=str('img/' + str(user.file))) for user in DBsession.query(Users_pictures).filter(Users_pictures.user_id == user_id)]
        print(users_files)
        count = [i for i in range(1, len(users_files) + 1)]
        user_pict = user_me.file
        name = user_me.name
        surname = user_me.surname
        about = user_me.about
        sex = user_me.sex
        filename = str('img/' + str(user_id) + '.jpg')
        return render_template('profile_page.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, users_files=users_files, count=count)
    return('Sosi')


@app.route('/account/<int:user_id>/mail_page', methods=['GET', 'POST'])
def account_mail(user_id):
    form = MailForm()
    # if check_user(user_id):
    #    return 'success'
    # return 'error'
    db_session.global_init("db/ff.sqlite")
    DBsession = db_session.create_session()
    user_me = DBsession.query(User).filter(User.id == user_id).first()
    user_pict = user_me.file
    name = user_me.name
    surname = user_me.surname
    about = user_me.about
    sex = user_me.sex
    filename = str('img/' + str(user_id) + '.jpg')
    whom = form.directionform.data
    if form.validate_on_submit():
        return redirect(url_for('account_mail_chat', user_id=user_id, whom=whom))
    return render_template('profile_mail.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id, form=form)


@app.route('/account/<int:user_id>/mail_page/<int:whom>', methods=['GET', 'POST'])
def account_mail_chat(user_id, whom):
    db_session.global_init("db/ff.sqlite")
    DBsession = db_session.create_session()
    user_me = DBsession.query(User).filter(User.id == user_id).first()
    user_pict = user_me.file
    name = user_me.name
    surname = user_me.surname
    about = user_me.about
    sex = user_me.sex
    filename = str('img/' + str(user_id) + '.jpg')
    whom_name = DBsession.query(User).filter(User.id == whom).first().name
    form = MailFormChat()
    # if check_user(user_id):
    #    return 'success'
    # return 'error'
    user_me = DBsession.query(User).filter(User.id == user_id).first()
    user_pict = user_me.file
    name = user_me.name
    surname = user_me.surname
    about = user_me.about
    sex = user_me.sex
    filename = str('img/' + str(user_id) + '.jpg')
    text = None
    db_session.global_init("db/message_to_chat.sqlite")
    DBsession = db_session.create_session()
    messages_gotten = []
    for i in DBsession.query(Message_to_chat).filter(Message_to_chat.id):
        if i.chat_id == user_id and i.direction == whom:
            messages_gotten.append(name + ': ' + i.message)
        if i.direction == user_id and i.chat_id == whom:
            messages_gotten.append(whom_name + ': ' + i.message)
    print(messages_gotten)
    #messages_gotten = ' '.join(messages_gotten)
    if form.validate_on_submit():
        message_to_chat = Message_to_chat()
        for i in DBsession.query(Message_to_chat).filter(Message_to_chat.id):
            message_to_chat.id = i.id + 1
        message_to_chat.chat_id = user_id
        message_to_chat.message = form.messageform.data
        message_to_chat.direction = whom
        DBsession.add(message_to_chat)
        DBsession.commit()
        return render_template('profile_mail_chat.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id, whom=whom, form=form, messages_gotten=messages_gotten)
    return render_template('profile_mail_chat.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id, whom=whom, form=form, messages_gotten=messages_gotten)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = 0
    return redirect('/')


@app.route('/account/<int:user_id>/search_page', methods=['GET', 'POST'])
def account_search(user_id):
    if check_user(user_id):
        return 'success'
    return 'error'
    # db_session.global_init("db/ff.sqlite")
    #DBsession = db_session.create_session()
    #user_me = DBsession.query(User).filter(User.id == user_id).first()
    #user_pict = user_me.file
    #name = user_me.name
    #surname = user_me.surname
    #about = user_me.about
    #sex = user_me.sex
    #filename = str('img/' + str(user_id) + '.jpg')
    # return render_template('profile_search.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id)


if __name__ == '__main__':
    db_session.global_init("db/ff.sqlite")
    app.run(debug=True, port=8089, host='127.0.0.1')
