# -*- coding: utf-8 -*-

import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


# 各種設定
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# アプリ生成
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# DB周り
# DB接続
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# DBの初期化
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

# リクエストに対する前処理
@app.before_request
def before_request():
    g.db = connect_db()

# リクエストに対する後処理
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# View
# エントリーページ
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

# エントリー追加
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash(u'新しいエントリーが追加されました')
    return redirect(url_for('show_entries'))

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = u'ユーザ名が間違っています'
        elif request.form['password'] != app.config['PASSWORD']:
            error = u'パスワードが間違っています'
        else:
            session['logged_in'] = True
            flash(u'ログインしました')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

# ログアウト
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'ログアウトしました')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
