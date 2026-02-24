
import sqlite3
import os

db_path = 'd:\\6th Sem\\Project\\AuraFace\\sql_app.db'
print(f'Connecting to {db_path}')

if not os.path.exists(db_path):
    print('DB not found!')
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check subjects table info
print('Checking subjects table...')
c = cursor.execute('PRAGMA table_info(subjects)')
cols = [row[1] for row in c.fetchall()]
print(f'Columns: {cols}')

if 'credits' not in cols:
    print('Adding credits column...')
    cursor.execute('ALTER TABLE subjects ADD COLUMN credits INTEGER DEFAULT 3')
    conn.commit()
    print('Column added.')
else:
    print('credits column already exists.')

conn.close()

