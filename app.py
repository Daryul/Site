from flask import Flask, render_template, request, session, redirect, url_for, make_response, g
import sqlite3
import hmac
import hashlib
import json
import base64
import time
import secrets
import bcrypt
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Функция для подключения к БД
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('DataBase.db')
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Login = request.form.get('Login')
        Password = request.form.get('Password')

        db = get_db()
        cursor_db = db.cursor()

        # БЕЗОПАСНЫЙ запрос (без SQL-инъекций)
        cursor_db.execute("SELECT password FROM passwords WHERE login = ?", (Login,))
        pas = cursor_db.fetchone()  # Используем fetchone вместо fetchall

        if pas and pas[0] == Password:
            # Пароль верный
            response = make_response(redirect('/Home'))
            # Устанавливаем куку
            setcookie('user_login', Login, age=3600, response=response)
            return response
        else:
            return render_template('login-bad.html')

    return render_template('login.html')


@app.route('/registration', methods=['GET', 'POST'])
def form_registration():
    if request.method == 'POST':
        Login = request.form.get('Login')
        Password = request.form.get('Password')

        db = get_db()
        cursor_db = db.cursor()

        try:
            # БЕЗОПАСНЫЙ запрос
            cursor_db.execute(
                "INSERT INTO passwords (login, password) VALUES (?, ?)",
                (Login, Password)
            )
            db.commit()
            return render_template('successfulregist.html')
        except sqlite3.IntegrityError:
            return render_template('bad-user.html')
        except Exception as e:
            return f"Ошибка: {e}"

    return render_template('registration.html')

@app.route('/Home')
def index():
    Login = getcookie('user_login')
    if not Login:
        return redirect('/')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT is_admin FROM passwords WHERE login = ?", (Login,))
    result = cursor.fetchone()
    is_admin = result[0] if result else 0
    news = cursor.execute("SELECT * FROM news ORDER BY number DESC").fetchall()
    last_news = cursor.execute(
    "SELECT * FROM news WHERE number = (SELECT MAX(number) FROM news)").fetchone()
    return render_template('index.html', Login=Login, is_admin=is_admin, news = news, last_news = last_news)


@app.route('/profile')
def profile():
    Login = getcookie('user_login')
    if not Login:
        return redirect('/')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT is_admin FROM passwords WHERE login = ?", (Login,))
    result = cursor.fetchone()
    lotteries = cursor.execute("SELECT * FROM lotteries").fetchall()
    is_admin = result[0] if result else 0
    return render_template('profile.html', Login=Login, is_admin=is_admin, lotteries=lotteries)

@app.route('/practicaljokes')
def loteries():
    Login = getcookie('user_login')
    if not Login:
        return redirect('/')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT is_admin FROM passwords WHERE login = ?", (Login,))
    result = cursor.fetchone()
    is_admin = result[0] if result else 0
    lotteries = cursor.execute("SELECT * FROM lotteries").fetchall()
    last_lotery = cursor.execute("SELECT * FROM lotteries WHERE number = (SELECT MAX(number) FROM lotteries)").fetchone()
    return render_template('loteries.html', Login=Login, is_admin=is_admin, lotteries=lotteries, last_lotery=last_lotery)


@app.route('/newLotery', methods=['GET', 'POST'])
def new_lotery():
    Login = getcookie('user_login')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT is_admin FROM passwords WHERE login = ?", (Login,))
    result = cursor.fetchone()
    is_admin = result[0] if result else 0
    if not Login or is_admin == False:
        return redirect('/')
    if request.method == 'POST':
        name = request.form['lotery_name']
        content = request.form['lotery_content']
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO lotteries (name, participants, content, winner) VALUES (?, ?, ?, ?)",
                           (name, 'none', content, 'none'))
            db.commit()
            return render_template('new-lotery.html', Login=Login, is_admin=is_admin)
        except sqlite3.IntegrityError:
            return "Розыгрыш уже существует"
        except Exception as e:
            return f"Ошибка: {e}"
    return render_template('new-lotery.html', Login=Login, is_admin=is_admin)

@app.route('/newnews', methods=['GET', 'POST'])
def new_news():
    Login = getcookie('user_login')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT is_admin FROM passwords WHERE login = ?", (Login,))
    result = cursor.fetchone()
    is_admin = result[0] if result else 0
    if not Login or is_admin == False:
        return redirect('/')
    if request.method == 'POST':
        name = request.form['news_name']
        content = request.form['news_content']
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO news (name, content) VALUES (?, ?)",
                           (name, content))
            db.commit()
            return render_template('new-news.html', Login=Login, is_admin=is_admin)
        except sqlite3.IntegrityError:
            return "Что-то пошло не так"
        except Exception as e:
            return f"Ошибка: {e}"
    return render_template('new-news.html', Login=Login, is_admin=is_admin)


@app.route('/menu-demo')
def menu_demo():
    return render_template('index.html')

@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.set_cookie('user_login', '', expires=0)
    return response

@app.route('/news/<int:news_number>')
def get_news(news_number):
    Login = getcookie('user_login')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM news WHERE number = ?", (news_number,))
    news = cursor.fetchone()
    cursor.execute("SELECT is_admin FROM passwords WHERE login = ?", (Login,))
    result = cursor.fetchone()
    is_admin = result[0] if result else 0
    if not Login:
        return redirect('/')
    return render_template('news.html', news = news, Login=Login, is_admin=is_admin)

@app.route('/practicaljokes/<int:lotery_number>')
def get_lotery(lotery_number):
    Login = getcookie('user_login')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM lotteries WHERE number = ?", (lotery_number,))
    lotery = cursor.fetchone()
    cursor.execute("SELECT is_admin FROM passwords WHERE login = ?", (Login,))
    result = cursor.fetchone()
    is_admin = result[0] if result else 0
    if not Login:
        return redirect('/')
    return render_template('lotery.html', lotery = lotery, Login=Login, is_admin=is_admin)

def setcookie(key, value, age=None, response=None):
    """Безопасная установка куки"""
    # Создаем подписанные данные
    data = {
        'value': value,
        'timestamp': int(time.time())
    }

    # Кодируем и подписываем
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    signature = hmac.new(
        app.secret_key.encode(),
        encoded.encode(),
        hashlib.sha256
    ).hexdigest()

    cookie_value = f"{encoded}.{signature}"

    if response is None:
        response = make_response()

    response.set_cookie(
        key,
        cookie_value,
        max_age=age,
        httponly=True,
        secure=True,  # False для localhost, True для production
        samesite='Strict'
    )
    return response


def getcookie(key):
    """Безопасное получение куки"""
    # Используем request из контекста Flask
    from flask import request
    cookie_value = request.cookies.get(key)

    if not cookie_value:
        return None

    try:
        # Разделяем данные и подпись
        encoded, signature = cookie_value.rsplit('.', 1)

        # Проверяем подпись
        expected = hmac.new(
            app.secret_key.encode(),
            encoded.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return None

        # Декодируем данные
        data = json.loads(base64.b64decode(encoded).decode())

        # Проверяем срок (например, 7 дней)
        if time.time() - data['timestamp'] > 7 * 24 * 60 * 60:
            return None

        return data['value']

    except (ValueError, json.JSONDecodeError, base64.binascii.Error):
        return None


if __name__ == '__main__':
    # Создаем таблицу если не существует
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                login TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0)
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lotteries (
                number INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL PRIMARY KEY,
                participants TEXT NOT NULL,
                content TEXT NOT NULL,
                winner TEXT NOT NULL)
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
            number INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL)
        ''')
        db.commit()
    app.run(debug=False)