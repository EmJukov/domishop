#Все импорты
from cloudipsp import Api, Checkout
from flask import Flask, render_template
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash
from data import db_session
from data.prices import Jobs, JobsForm
from data.users import User, LoginForm, RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_ngrok import run_with_ngrok

#конфигурация приложения
app = Flask(__name__)
run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/blogs.db")
db_sess = db_session.create_session()

#основная страница
@app.route('/')
def base():
    if current_user.is_authenticated:
        a = [(repr(user)).split('/') for user in db_sess.query(Jobs).all()]
        return render_template('main.html', title='Главная', user_list=a, id_user=str(current_user.id))
    return render_template('main.html', title='Главная')


#страница оплаты
@app.route('/buy/<int:id>')
def item_buy(id):
    item = db_sess.query(Jobs).get(id)
    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.work_size) + '00'
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)

#выход из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

#страница входа в аккаунт
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


#страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def reg():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User()
        new_user.email = form.email.data
        new_user.hashed_password = generate_password_hash(form.password.data)
        new_user.surname = form.surname.data
        new_user.name = form.name.data
        new_user.age = form.age.data
        new_user.position = form.position.data
        new_user.address = form.address.data
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            return render_template('register.html',
                                   message="Аккаунт уже существует",
                                   form=form)
        db_sess.add(new_user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация',
                           form=form)


#страница добавления объявления
@app.route('/jobs_add', methods=['GET', 'POST'])
@login_required
def add_news():
    form = JobsForm()
    if form.validate_on_submit():
        news = Jobs()
        news.team_leader = current_user.id
        news.job = form.job.data
        news.work_size = form.work_size.data
        news.collaborators = form.collaborators.data
        news.start_date = form.start_date.data
        news.end_date = form.end_date.data
        news.is_finished = form.is_finished.data
        db_sess.add(news)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', title='Добавление объявления',
                           form=form)


#редактирование объявления
@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobsForm()
    id = int(id)
    a = [user for user in db_sess.query(Jobs).filter(id == Jobs.id)]
    if not list(a):
        return redirect('/')
    if current_user.id != a[0].team_leader and current_user.id != 1:
        return redirect('/')
    if form.validate_on_submit():
        a[0].job = form.job.data
        a[0].work_size = form.work_size.data
        a[0].collaborators = form.collaborators.data
        a[0].start_date = form.start_date.data
        a[0].end_date = form.end_date.data
        a[0].is_finished = form.is_finished.data
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', title='Редактирование объявления',
                           form=form)


#удаление объявления
@app.route('/jobs/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_jobs(id):
    a = [user for user in db_sess.query(Jobs).filter(id == Jobs.id)]
    if not list(a):
        abort(404)
        return
    if current_user.id != a[0].team_leader and current_user.id != 1:
        return redirect('/')
    db_sess.delete(a[0])
    db_sess.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run()
