import sqlite3

db_path = "attendance.db"

def try_add_column(cursor, table, column, definition):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"Added {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding {column} to {table}: {e}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try_add_column(cursor, "placement_skills", "document_url", "VARCHAR")
    try_add_column(cursor, "placement_internships", "document_url", "VARCHAR")
    try_add_column(cursor, "placement_projects", "document_url", "VARCHAR")
    try_add_column(cursor, "placement_events", "document_url", "VARCHAR")

    conn.commit()
    conn.close()
    
    print("Placement tracking DB migration completed.")
except Exception as e:
    print(f"Error: {e}")
