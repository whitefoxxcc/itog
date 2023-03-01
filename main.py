from flask import Flask, g, render_template, request, session, redirect, url_for, abort, flash
import sqlite3
import os
from FDataBase import FDataBase

# конфигураци
DATABASE = '/tmp/main.db'
DEBUG = True
SECRET_KEY = '1234567'


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '123456'     #вот эта вот надо потом переделать чтобы оно само чето генерировало

app.config.update(DATABASE=os.path.join(app.root_path, 'main.db'))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """соединение с БД, если оно ещё не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route('/')
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', title='Сайт о здоровом образе жизни', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route('/add_post', methods=["POST", 'GET'])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title='Добавление статьи')


@app.route('/post/<alias>')
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route('/about')
def about():
    return render_template('about.html', title='О сайте', menu=[])


@app.route('/login', methods=['POST', 'GET'])      # хуй знает ваще как эта поебота работает я со стек оверфлоу скопировал
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session["userLogged"]))
    elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form['psw'] == '123':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title='Авторизация', menu=[])


@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Профиль пользователя {username}'


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', menu=[])


@app.teardown_appcontext
def close_db(error):
    """закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


if __name__ == '__main__':
    app.run(debug=True)