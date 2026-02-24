
import sqlite3
import os

# Try default SQLAlchemy name 'attendance.db' since 'sql_app.db' was missing
db_paths = ['attendance.db', 'auraface.db']

for db_path in db_paths:
    full_path = os.path.join(os.getcwd(), db_path)
    if os.path.exists(full_path):
        print(f'Prforming checks on {full_path}')
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(\
SELECT
name
FROM
sqlite_master
WHERE
type=table
AND
name=subjects\)
        if not cursor.fetchone():
            print(f'Table subjects does not exist in {db_path}. Skipping.')
            conn.close()
            continue

        c = cursor.execute('PRAGMA table_info(subjects)')
        cols = [row[1] for row in c.fetchall()]
        print(f'Columns in {db_path}: {cols}')

        if 'credits' not in cols:
            print(f'Adding credits column to {db_path}...')
            try:
                cursor.execute('ALTER TABLE subjects ADD COLUMN credits INTEGER DEFAULT 3')
                conn.commit()
                print('Column added successfully.')
            except Exception as e:
                print(f'Error adding column: {e}')
        else:
            print(f'credits column already exists in {db_path}.')
        
        conn.close()

