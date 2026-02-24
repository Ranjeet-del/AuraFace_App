
import sqlite3
import os

files = [f for f in os.listdir('.') if f.endswith('.db')]
print(f'Found DB files: {files}')

for db_file in files:
    try:
        print(f'\\nChecking {db_file}...')
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        # Check if table exists
        c.execute(\
SELECT
name
FROM
sqlite_master
WHERE
type=table
AND
name=subjects\)
        if not c.fetchone():
            print(f'Table subjects NOT found in {db_file}')
            continue
            
        print(f'Table subjects found in {db_file}')
        c.execute('PRAGMA table_info(subjects)')
        cols = [r[1] for r in c.fetchall()]
        print(f'Columns: {cols}')
        
        if 'credits' not in cols:
            print('Adding credits column...')
            c.execute('ALTER TABLE subjects ADD COLUMN credits INTEGER DEFAULT 3')
            conn.commit()
            print('Success')
        else:
            print('credits column already present')
            
        conn.close()
    except Exception as e:
        print(f'Error: {e}')

