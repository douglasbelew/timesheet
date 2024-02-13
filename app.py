import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_line_item(id):
    conn = get_db_connection()
    lineItems = conn.execute('SELECT * FROM LineItem WHERE id = ?',
                        (id,)).fetchone()
    conn.close()
    if lineItems is None:
        abort(404)
    return lineItems

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    conn = get_db_connection()
    lineItems = conn.execute('SELECT * FROM lineItem').fetchall()
    conn.close()
    return render_template('index.html', lineItems=lineItems)

@app.route('/<int:id>')
def lineItem(id):
    lineItem = get_line_item(id)
    return render_template('lineItem.html', lineItem=lineItem)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        lineItemDate = request.form['lineItemDate']
        lineItemMinutes = request.form['lineItemMinutes']
        description = request.form['description']

        if not lineItemDate:
            flash('Line Item Date is required!')
        else:
            conn = get_db_connection()

            conn.execute ("INSERT INTO LineItem (lineItemDate, lineItemMinutes, description) VALUES (?, ?, ?)",
                         (lineItemDate, lineItemMinutes, description))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    lineItem = get_line_item(id)

    if request.method == 'POST':
        lineItemDate = request.form['lineItemDate']
        lineItemMinutes = request.form['lineItemMinutes']
        description = request.form['description']

        if not lineItemDate:
            flash('Line Item Date is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE LineItem SET lineItemDate = ?, lineItemMinutes = ?, description = ?'
                         ' WHERE id = ?',
                         (lineItemDate, lineItemMinutes, description, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', lineItem=lineItem)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    lineItem = get_line_item(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM LineItem WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(LineItem['lineItemDate']))
    return redirect(url_for('index'))
