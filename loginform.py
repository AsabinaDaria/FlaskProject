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
import hashlib
import binascii
import os
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
Bootstrap(app)
auth = HTTPBasicAuth()
engine = create_engine('sqlite:///ff.db', echo=True)
#login = LoginManager(app)
#DBSession = sessionmaker(bind=engine)
#db_session = DBSession()


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
# username=form.login.data[:form.login.data.find('@')]),
# print(url_for('account', user_id=user_id,  username=username)

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
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
        user_data = DBsession.query(User).filter(User.login == form.login.data).first()
        if user_data:
            password = user_data.password
            if verify_password(password, form.password.data) == True:
                #s = requests.db_session()
                #cookies = s.cookies.items()
                #s.cookies.set('id', user_data.id)
                #res = make_response(render_template('account_page', user_id=user_id))
                #res.set_cookie('id', str(user_data.id))
                #print(s.cookies.get('id'))
            #if db_session.query(User).filter(User.password == form.password.data).first():
                user_me = DBsession.query(User).filter_by(
                    login=form.login.data).first()
                user_id = user_me.id
                #res = make_response('')
                #res.set_cookie('id', str(user_data.id))
                #res.headers['location'] = url_for('account_page', user_id=user_id)
                #print(res)
                #Session = sessionmaker(bind=engine)
                #s = sessionmaker()
                session['logged_in'] = user_data.id
                return redirect(url_for('account_page', user_id=user_id))
            else:
                print(password)
                return render_template('home.html', title='Вход', form=form, message="Неверно указан пароль")
        else:
            return render_template('home.html', title='Вход', form=form, message="Неверно указан логин")
        user_me = DBsession.query(User).filter_by(login=form.login.data).first()
        user_id = user_me.id
        session['logged_in'] = str(user_data.id)
        print(session.get('logged_in'))
        return redirect(url_for('account_page', user_id=user_id))
    return render_template('home.html', title='Вход', form=form)


def check_user(user_id):
    if 'logged_in' in session:
        print(session.get('logged_in'))
        if user_id == session.get('logged_in'):
            return True
        print('error')
        return False
    return False


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
        DBsession = db_session.create_session()
        if DBsession.query(User).filter(User.login == form.login.data).first():
            print(7)
            return render_template('login.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        print(999)

        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.login = form.login.data
        user.password = hash_password(form.password.data)
        #user.password = storage
        user.about = form.about.data
        # user.file = filename
        user.sex = form.sex.data
        user.remember_me = form.remember_me.data
        db_session = DBsession.create_session()
        DBsession.add(user)
        DBsession.commit()
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)
        photo = str(user.id) + str(file_extension[1])
        file.save(os.path.join(
            "C:/Users/я/Downloads/FlaskProject-master-Alex/FlaskProject-master/static/img/", photo))
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
        user_pict = user_me.file
        name = user_me.name
        surname = user_me.surname
        about = user_me.about
        sex = user_me.sex
        filename = str('img/' + str(user_id) + '.jpg')
        return render_template('profile_page.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex)
    return('Sosi')


@app.route('/account/<int:user_id>/mail_page', methods=['GET', 'POST'])
def account_mail(user_id):
    if check_user(user_id):
        return 'success'
    return 'error'
    #db_session.global_init("db/ff.sqlite")
    #DBsession = db_session.create_session()
    #user_me = DBsession.query(User).filter(User.id == user_id).first()
    #user_pict = user_me.file
    #name = user_me.name
    #surname = user_me.surname
    #about = user_me.about
    #sex = user_me.sex
    #filename = str('img/' + str(user_id) + '.jpg')
    #return render_template('profile_mail.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = 0
    return redirect('/')


@app.route('/account/<int:user_id>/search_page', methods=['GET', 'POST'])
def account_search(user_id):
    if check_user(user_id):
        return 'success'
    return 'error'
    #db_session.global_init("db/ff.sqlite")
    #DBsession = db_session.create_session()
    #user_me = DBsession.query(User).filter(User.id == user_id).first()
    #user_pict = user_me.file
    #name = user_me.name
    #surname = user_me.surname
    #about = user_me.about
    #sex = user_me.sex
    #filename = str('img/' + str(user_id) + '.jpg')
    #return render_template('profile_search.html', title=name, name=name, surname=surname, file=url_for('static', filename=filename), about=about, sex=sex, user_id=user_id)



if __name__ == '__main__':
    app.run(debug=True, port=8088, host='127.0.0.1')
