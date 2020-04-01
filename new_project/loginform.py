from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import *
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
Bootstrap(app)


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

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
					    <a href="/login">Login</a>
					</div>
			  </body>
			</html>"""


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/success', methods=['GET', 'POST'])
def l():
	return """<!doctype html>
                <html>
                <body>
                 <h1>Тут весь движ</h1>
                    </div>
                    <div>
					    Microblog:
					    <a href="/">Home</a>
					    <a href="/login">Login</a>
					</div>
			  </body>
			</html>"""



if __name__ == '__main__':
    app.run(port=8081, host='127.0.0.1')