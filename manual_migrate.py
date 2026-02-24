
import sqlite3

try:
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('ALTER TABLE subjects ADD COLUMN credits INTEGER DEFAULT 3')
    conn.commit()
    print('Added credits to attendance.db')
except Exception as e:
    print(f'attendance.db: {e}')

try:
    conn = sqlite3.connect('auraface.db')
    c = conn.cursor()
    c.execute('ALTER TABLE subjects ADD COLUMN credits INTEGER DEFAULT 3')
    conn.commit()
    print('Added credits to auraface.db')
except Exception as e:
    print(f'auraface.db: {e}')

