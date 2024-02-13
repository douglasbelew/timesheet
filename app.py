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
    #timeSheets = conn.execute('SELECT * FROM TimeSheet').fetchall()

    timeSheets = conn.execute('SELECT sum(lineItemMinutes)totalMinutes, TimeSheet.* \
	FROM TimeSheet \
        LEFT OUTER JOIN LineItem \
	ON LineItem.timeSheet_id = TimeSheet.id \
        GROUP BY TimeSheet.id \
    ').fetchall()
    conn.close()
    return render_template('index.html', timeSheets=timeSheets)

@app.route('/timeSheet/<int:id>', methods=('GET', 'POST'))
def timeSheet(id):
    if request.method == 'POST':
       
         conn = get_db_connection()
         conn.execute ("update TimeSheet set hourlyRate = ? where id = ?",
                         (request.form['hourlyRate'], request.form['timeSheet_id'] ))
         conn.commit()
         conn.close()

    conn = get_db_connection()
    timeSheet = conn.execute('SELECT * FROM TimeSheet where id = ?', (id, )).fetchone()
    lineItems = conn.execute('SELECT * FROM LineItem where timesheet_id = ?', (id, )).fetchall()
    conn.close()
    return render_template('timeSheet.html', lineItems=lineItems, timeSheet = timeSheet)

@app.route('/<int:id>')
def lineItem(id):
    lineItem = get_line_item(id)
    return render_template('lineItem.html', lineItem=lineItem)

@app.route('/createTimeSheet', methods=('GET', 'POST'))
def createTimeSheet():
    if request.method == 'POST':
        submittedDate = request.form['submittedDate']
        description = request.form['description']
        hourlyRate = request.form['hourlyRate']

        if not submittedDate:
            flash('Submitted Date is required!')
        else:
            conn = get_db_connection()

            conn.execute ("INSERT INTO TimeSheet (submittedDate, hourlyRate, description) VALUES (?, ?, ?)",
                         (submittedDate, hourlyRate, description))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('createTimeSheet.html')

@app.route('/timeSheet/<int:timeSheet_id>/create', methods=('GET', 'POST'))
def create(timeSheet_id):
    if request.method == 'POST':
        lineItemDate = request.form['lineItemDate']
        lineItemMinutes = request.form['lineItemMinutes']
        description = request.form['description']
        timeSheet_id = request.form['timeSheet_id']

        if not lineItemDate:
            flash('Line Item Date is required!')
        else:
            conn = get_db_connection()

            conn.execute ("INSERT INTO LineItem (timeSheet_id, lineItemDate, lineItemMinutes, description) VALUES (?, ?, ?, ?)",
                         (timeSheet_id, lineItemDate, lineItemMinutes, description))
            conn.commit()
            conn.close()
            return redirect(url_for('timeSheet', id = request.form['timeSheet_id']))

    return render_template('create.html', timeSheet_id = timeSheet_id)

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
    flash('"{}" was successfully deleted!'.format(lineItem['lineItemDate']))
    return redirect(url_for('index'))
