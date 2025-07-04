import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
# TODO use for db path http://flask.pocoo.org/docs/0.12/config/#instance-folders
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

# FLASKR_SETTINGS points to a config file
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('init_db')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
@app.route('/')
def show_entries():
    try:
        db = get_db()
        cur = db.execute('SELECT id, title, text FROM entries ORDER BY id DESC')
        entries = cur.fetchall()
    except sqlite3.Error as e:
        # Log the error
        app.logger.error(f"Database error: {e}")
        entries = []
    return render_template('show_entries.html', entries=entries)
g.sqlite_db.close()


# SQL query constant
ENTRIES_SELECT_QUERY = 'SELECT id, title, text FROM entries ORDER BY id DESC'

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute(ENTRIES_SELECT_QUERY)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('INSERT INTO entries (title, text) VALUES (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/remove/<int:entry_id>', methods=['POST'])
@app.route('/remove/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
if not session.get('logged_in'):
        abort(401)
    db = get_db()
    try:
        db.execute('DELETE FROM entries WHERE id = ?', [entry_id])
        db.commit()
        flash('Entry was successfully removed')
    except sqlite3.Error as e:
        db.rollback()
        flash(f'Error removing entry: {str(e)}')
    return redirect(url_for('show_entries'))
    db.commit()
    flash('Entry was successfully removed')
    return redirect(url_for('show_entries'))
