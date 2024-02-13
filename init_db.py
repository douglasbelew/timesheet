import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO TimeSheet (description, hourlyRate) VALUES (?, ?)",
           ('Timesheet for X', '100')
)

cur.execute("INSERT INTO LineItem (timeSheet_id, lineItemDate, lineItemMinutes, description) VALUES (?, ?, ?, ?)",
           (1, '2024-01-01', '100', 'some work')
)

cur.execute("INSERT INTO LineItem (timeSheet_id, lineItemDate, lineItemMinutes, description) VALUES (?, ?, ?, ?)",
           (1, '2024-01-02', '200', 'more work')
)

connection.commit()
connection.close()
