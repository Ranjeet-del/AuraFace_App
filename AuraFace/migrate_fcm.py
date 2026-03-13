import sqlite3
import os

def upgrade():
    db_file = "attendance.db"
    
    if not os.path.exists(db_file):
        print(f"Database {db_file} not found. Skipping migration (will be created by create_all).")
        return

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if column exists in users
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "fcm_token" not in columns:
            print("Adding fcm_token to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN fcm_token TEXT")
        else:
            print("fcm_token already exists in users.")

        conn.commit()
        conn.close()
        print("Manual migration attempt complete.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    upgrade()
