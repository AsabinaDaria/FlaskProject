from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask import *
from flask_bootstrap import Bootstrap
from data import db_session
from flask import *
from data.db_session import *
from data import db_session
from data.users import *
from data.users_pictures import *
from data.message_to_chat import *
import requests
import os
from flask_wtf.file import *
from werkzeug.utils import *
import hashlib
import binascii
import sqlite3
from sqlalchemy.orm import sessionmaker
import random
#from flask_ngrok import run_with_ngrok


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ff.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
#run_with_ngrok(app)


# класс с формой для регистрации
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


# класс с формой для настроек профиля
class SettingsForm(FlaskForm):
    name = StringField('Имя', validators=None)
    surname = StringField('Фамилия', validators=None)
    login = StringField('Логин', validators=None)
    password = PasswordField('Пароль', validators=[DataRequired()])
    about = TextAreaField('Статус', validators=None)
    file = FileField(validators=None)
    #file = FileField(validators=[FileRequired()])
    sex = SelectField('Укажите Ваш пол:', choices=[
                      ('1', 'женский'), ('2', 'мужской')], validators=None)
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Регистрация')


# класс с формой для входа в аккаунт
class HomeForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


# класс с формой для выбора собеседника в чате
class MailForm(FlaskForm):
    directionform = StringField('кому', validators=[DataRequired()])
    submit = SubmitField('Войти')


# класс с формой для отправки сообщений в чате
class MailFormChat(FlaskForm):
    messageform = PasswordField('сообщение', validators=[DataRequired()])
    submit = SubmitField('Войти')


# класс с формой для поиска информации о введенной локации
class SearchForm(FlaskForm):
    searchform = StringField('кому', validators=[DataRequired()])
    submit = SubmitField('Войти')


# функция для хэширования паролей
def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


# функция для сравнения паролей
def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


# страница входа в аккаунт
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
                if "logged_in" not in session:
                    session['logged_in'] = [user_data.id]
                else:
                    if session.get('logged_in') == [0]:
                        session['logged_in'] = [user_data.id]
                    else:
                        the_order_list = session['logged_in']
                        the_order_list.append(user_data.id)
                        session['logged_in'] = the_order_list
                    # переадресация на профиль, если введенные данные верны
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
    # проверка на то, авторизирован ли пользователь
    if 'logged_in' in session:
        the_order_list = session['logged_in']
        for e in the_order_list:
            if str(user_id) == str(e):
                return True
    return False


# регистрация
@app.route('/register', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        global db_session
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        if form.password.data != form.password_again.data:
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
        file.save("static/img/" + photo)
        user.file = photo
        DBsession.commit()
        # добаление пользователя и переадресация на домашнюю страницу
        return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)


# профиль пользователя
@app.route('/account/<int:user_id>/acc_page', methods=['GET', 'POST'])
def account_page(user_id):
    db_session.global_init("db/ff.sqlite")
    DBsession = db_session.create_session()
    user_me = DBsession.query(User).filter(User.id == user_id).first()
    users_files = [url_for('static', filename=str('img/' + str(user.file)))
                   for user in DBsession.query(Users_pictures).filter(Users_pictures.user_id == user_id)]
    count = [i for i in range(1, len(users_files) + 1)]
    if len(users_files) == 0:
        count = 0
    user_pict = user_me.file
    name = user_me.name
    surname = user_me.surname
    about = user_me.about
    sex = user_me.sex
    if str(user_me.file) != str(user_id):
        filename = str('img/' + str(user_id) + '.jpg')
    else:
        filename = str('img/' + str(0) + '.jpg')
    if check_user(user_id):
        return render_template('profile_page.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, users_files=users_files, count=count)
    return render_template('profile_page_another.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, users_files='Фото может видеть только авторизированный пользователь', count=1010)


# почта пользователя
@app.route('/account/<int:user_id>/mail_page', methods=['GET', 'POST'])
def account_mail(user_id):
    form = MailForm()
    if check_user(user_id):
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        user_me = DBsession.query(User).filter(User.id == user_id).first()
        user_pict = user_me.file
        name = user_me.name
        surname = user_me.surname
        about = user_me.about
        sex = user_me.sex
        if str(user_me.file) != str(user_id):
            filename = str('img/' + str(user_id) + '.jpg')
        else:
            filename = str('img/' + str(0) + '.jpg')
        user_me = DBsession.query(User).filter(User.id == user_id).first()
        whom = form.directionform.data
        if form.validate_on_submit():
            form.directionform.data = None
            try:
                return redirect(url_for('account_mail_chat', user_id=user_id, whom=whom))
            except:
                return redirect(url_for('account_mail', user_id=user_id))
        return render_template('profile_mail.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id, form=form)
    if not check_user(user_id):
        return redirect('/')


# переписка пользователя
@app.route('/account/<int:user_id>/mail_page/<int:whom>', methods=['GET', 'POST'])
def account_mail_chat(user_id, whom):
    if check_user(user_id):
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        user_me = DBsession.query(User).filter(User.id == user_id).first()
        user_pict = user_me.file
        name = user_me.name
        surname = user_me.surname
        about = user_me.about
        sex = user_me.sex
        filename = str('img/' + str(user_id) + '.jpg')
        try:
            whom_name = DBsession.query(User).filter(
                User.id == whom).first().name
        except:
            return redirect(url_for('account_mail', user_id=user_id))
        form = MailFormChat()
        user_me = DBsession.query(User).filter(User.id == user_id).first()
        user_pict = user_me.file
        name = user_me.name
        surname = user_me.surname
        about = user_me.about
        sex = user_me.sex
        if str(user_me.file) != str(user_id):
            filename = str('img/' + str(user_id) + '.jpg')
        else:
            filename = str('img/' + str(0) + '.jpg')
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
        if form.validate_on_submit():
            message_to_chat = Message_to_chat()
            for i in DBsession.query(Message_to_chat).filter(Message_to_chat.id):
                message_to_chat.id = i.id + 1
            message_to_chat.chat_id = user_id
            message_to_chat.message = form.messageform.data
            message_to_chat.direction = whom
            DBsession.add(message_to_chat)
            DBsession.commit()
            return redirect(url_for('account_mail', user_id=user_id))
        return render_template('profile_mail_chat.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id, whom=whom, form=form, messages_gotten=messages_gotten)
    if not check_user(user_id):
        return redirect('/')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # выход из аккаунта пользователя
    session['logged_in'] = [0]
    return redirect('/')


# поиск информации о локации
@app.route('/account/<int:user_id>/search_page', methods=['GET', 'POST'])
def account_search(user_id):
    if check_user(user_id):
        form = SearchForm()
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        user_me = DBsession.query(User).filter(User.id == user_id).first()
        user_pict = user_me.file
        name = user_me.name
        surname = user_me.surname
        about = user_me.about
        sex = user_me.sex
        if str(user_me.file) != str(user_id):
            filename = str('img/' + str(user_id) + '.jpg')
        else:
            filename = str('img/' + str(0) + '.jpg')
        searched = form.searchform.data
        if form.validate_on_submit():
            form.searchform.data = None
            return redirect(url_for('account_searched', user_id=user_id, searched=searched))
        return render_template('profile_search.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id, form=form)
    return redirect('/')


# найденная информация о введенной локации
@app.route('/account/<int:user_id>/search_page/<string:searched>', methods=['GET', 'POST'])
def account_searched(user_id, searched):
    if check_user(user_id):
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        user_me = DBsession.query(User).filter(User.id == user_id).first()
        user_pict = user_me.file
        name = user_me.name
        surname = user_me.surname
        about = user_me.about
        sex = user_me.sex
        if str(user_me.file) != str(user_id):
            filename = str('img/' + str(user_id) + '.jpg')
        else:
            filename = str('img/' + str(0) + '.jpg')
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + \
            searched + "&format=json"
        response = requests.get(geocoder_request)
        json_response = response.json()
        try:
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        except:
            toponym = None
        try:
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        except:
            toponym_address = 'Невозможно найти полный адрес'
        try:
            toponym_coodrinates = toponym["Point"]["pos"]
        except:
            toponym_coodrinates = 'Невозможно найти координаты'
        try:
            postal_code = toponym["metaDataProperty"]['GeocoderMetaData']['Address']['postal_code']
        except:
            postal_code = 'Невозможно найти почтовый индекс'
        return render_template('profile_searched.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id, searched=searched, toponym_address=toponym_address, toponym_coodrinates=toponym_coodrinates, postal_code=postal_code)
    return redirect('/')


# настройки аккаунта
@app.route('/account/<int:user_id>/settings', methods=['GET', 'POST'])
def settings(user_id):
    if check_user(user_id):
        form = SettingsForm()
        if form.validate_on_submit():
            global db_session
            db_session.global_init("db/ff.sqlite")
            DBsession = db_session.create_session()
            user = DBsession.query(User).filter(User.id == user_id).first()
            if form.name.data:
                user.name = form.name.data
            if form.surname.data:
                user.surname = form.surname.data
            if form.login.data:
                user.login = form.login.data
            user.password = hash_password(form.password.data)
            if form.about.data:
                user.about = form.about.data
            if form.sex.data:
                user.sex = form.sex.data
            user.remember_me = form.remember_me.data
            DBsession.commit()
            if form.file.data:
                pictures = Users_pictures()
                file = request.files['file']
                filename = secure_filename(file.filename)
                file_extension = os.path.splitext(filename)
                my_value = int(str(user_id) + str(random.randint(1, 100000)))
                photo = str(my_value) + str(file_extension[1])
                file.save("static/img/" + photo)
                pictures.file = photo
                pictures.user_id = user.id
                DBsession = db_session.create_session()
                DBsession.add(pictures)
            DBsession.commit()
            # сохранение изменений и возврат на акаунт
            return redirect(url_for('account_page', user_id=user_id))
        db_session.global_init("db/ff.sqlite")
        DBsession = db_session.create_session()
        user_me = DBsession.query(User).filter(User.id == user_id).first()
        user_pict = user_me.file
        name = user_me.name
        surname = user_me.surname
        about = user_me.about
        sex = user_me.sex
        if str(user_me.file) != str(user_id):
            filename = str('img/' + str(user_id) + '.jpg')
        else:
            filename = str('img/' + str(0) + '.jpg')        
        return render_template('settings.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id, form=form)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=8081, host='127.0.0.1')