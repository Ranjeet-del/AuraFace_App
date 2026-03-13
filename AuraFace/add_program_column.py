import sqlite3
import sys

db_paths = ["auraface.db", "attendance.db"]
for path in db_paths:
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        
        # Check if column exists
        cur.execute("PRAGMA table_info(students);")
        columns = [row[1] for row in cur.fetchall()]
        if 'program' not in columns:
            cur.execute("ALTER TABLE students ADD COLUMN program VARCHAR;")
            print(f"Added column 'program' to students table in {path}")
            conn.commit()
        else:
            print(f"Column 'program' already exists in students table in {path}")
        
        conn.close()
    except Exception as e:
        print(f"Error migrating {path}: {e}")
