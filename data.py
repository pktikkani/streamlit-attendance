import sqlite3

conn = sqlite3.connect('attendance.db')
c = conn.cursor()

def create_attendance_table():
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
             (name TEXT, email TEXT, date TEXT)''')
    conn.commit()


