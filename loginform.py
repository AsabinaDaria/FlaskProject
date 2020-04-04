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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
Bootstrap(app)


class LoginForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    about = TextAreaField('Статус', validators=None)
    file = FileField('Аватарка', validators=None)
    sex = SelectField('Укажите Ваш пол:', choices=[('1', 'женский'), ('2', 'мужской')], validators=None)
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Регистрация')

@app.route('/')
def index():
    return """<!doctype html>
                <html>
                <body>
                 <h1>Чевота написано</h1>
                    </div>
                    <div>
					    Microblog:
					    <a href="/">Home</a>
					    <a href="/register">Register</a>
					</div>
			  </body>
			</html>"""


@app.route('/register', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_session.global_init("db/ff.sqlite")
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.login = form.login.data
        user.password = form.password.data
        user.about = form.about.data
        user.file = form.file.data
        user.sex = form.sex.data
        user.remember_me = form.remember_me.data
        session = db_session.create_session()
        session.add(user)
        session.commit()
        return redirect('/account_creation')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/account_creation', methods=['GET', 'POST'])
def account_creation():
    form = LoginForm()
    db_session.global_init("db/ff.sqlite")
    session = db_session.create_session()
    for user in session.query(User).all():
        print(user.password)
    return render_template('login.html', title='Авторизация', form=form)



@app.route('/success', methods=['GET', 'POST'])
def l():
    form = LoginForm()
    db_session.global_init("db/ff.sqlite")
    session = db_session.create_session()
    for user in session.query(User).all():
        print(user.password)
    return render_template('login.html', title='Авторизация', form=form)



if __name__ == '__main__':
    app.run(port=8087, host='127.0.0.1')