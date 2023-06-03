from flask import Flask, session, redirect, render_template, request, abort
import sqlite3

id = 1
id_n = 1
reg = False
reg2 = False
app = Flask(__name__)
app.secret_key = 'jrfasefasefgj'

def is_login():
    if session.get('auth', False) == True:
        return True
    else:
        abort(403)

def db_session(func):
    def wrapper(*args, **kwargs):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        result = None
        try:
            result = func(cursor, *args, **kwargs)
            connection.commit()
        except Exception as e:
            connection.close()
            print(e)
            abort(500)

        connection.close()
        return result
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/')
@db_session
def index(cur):
    if is_login():
        cur_id = session.get('id')
        id_note = f"Select user_id from notes where user_id = {cur_id}"
        print(id_note)
        if cur.execute(id_note).fetchone() is None:
            return render_template('index.html', topic=cur.execute("SELECT * FROM notes"))
        else:
            id_note2 = cur.execute(id_note).fetchone()[0]
            return render_template('index.html', topic=cur.execute("SELECT * FROM notes"), cur_id=cur_id, id_note=id_note2)
    else:
        return render_template('base.html')


@app.route('/login', methods=["POST", "GET"])
@db_session
def login(cur):
    if request.method == "POST":
        if cur.execute("SELECT * FROM users").fetchone() is None:
            return redirect("/reg")
        else:
            user = "SELECT * FROM users WHERE login = ?"
            if cur.execute(user, [request.form.get('login')]).fetchone() is not None:
                session['auth'] = True
                session['id'] = cur.execute(user, [request.form.get('login')]).fetchone()[0]
                return redirect("/")
            else:
                return "error"
    else:
        return render_template("login.html")


@app.route('/reg', methods=["POST", "GET"])
@db_session
def regi(cur):
    global reg
    if request.method == "POST":
        user = f"SELECT * FROM users WHERE login = '{request.form.get('login')}'"
        if cur.execute(user).fetchone() is None:
            login = request.form.get('login')
            password = request.form.get('password')
            cur.execute(f"""
                INSERT INTO users (login, password) VALUES
                    ({login!r}, {password!r})""")
            return redirect("/login")
        else:
            return "EROR! Такой пользователь уже есть!"

    else:
        return render_template('regi.html')


@app.route('/add', methods=["POST", "GET"])
@db_session
def add(cur):
    global reg2, id_n
    if is_login():
        if request.method == "POST":
            name = request.form["task_fun"]
            text = request.form["task_name"]
            user_name = session.get('id')
            query = f"""
                INSERT INTO notes (name, text, user_id) VALUES
                   (?, ?, ?)"""

            cur.execute(query, [name, text, user_name])
            id_n += 1
            return redirect("/")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/del/<int:id>')
@db_session
def dell(cur, id):
    if is_login():
        dell = f"""
        DELETE FROM notes
        WHERE id = {id} ;"""
        cur.execute(dell)
        return redirect('/')

@app.route('/edit/<int:id>')
@db_session
def edit(cur, id):
    if is_login():
        name = f"SELECT name FROM notes WHERE id = {id}"
        text = f"SELECT text FROM notes WHERE id = {id}"
        return render_template('edit2.html', task_id=id, name=cur.execute(name).fetchone()[0], text=cur.execute(text).fetchone()[0])

@app.route('/note/<int:id>/edit', methods=["POST", "GET"])
@db_session
def edit2(cur, id):
    name = request.form.get('name')
    text = request.form.get('text')

    upd_name = f"""
    UPDATE notes
    SET name = '{name}'
    WHERE id = {id};"""
    cur.execute(upd_name)

    upd_text = f"""
    UPDATE notes
    SET text = '{text}'
    WHERE id = {id};"""
    cur.execute(upd_text)
    return redirect('/')
app.run(debug=True)