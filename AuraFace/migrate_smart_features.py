import sqlite3
import os

def upgrade():
    db_file = "attendance.db"
    
    if not os.path.exists(db_file):
        print(f"Database {db_file} not found. Skipping migration.")
        return

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check columns in notices
        cursor.execute("PRAGMA table_info(notices)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "priority" not in columns:
            print("Adding priority to notices...")
            cursor.execute("ALTER TABLE notices ADD COLUMN priority TEXT DEFAULT 'LOW'")
            
        if "expiry_date" not in columns:
            print("Adding expiry_date to notices...")
            cursor.execute("ALTER TABLE notices ADD COLUMN expiry_date TIMESTAMP")

        # Create notice_reads table if not exists (Though create_all will do it, safe to do here)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notice_reads'")
        if not cursor.fetchone():
             print("Creating notice_reads table...")
             cursor.execute("""
                CREATE TABLE notice_reads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notice_id INTEGER,
                    user_id INTEGER,
                    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(notice_id) REFERENCES notices(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
             """)
             # Add index
             cursor.execute("CREATE INDEX idx_notice_reads_notice_id ON notice_reads (notice_id)")
             cursor.execute("CREATE INDEX idx_notice_reads_user_id ON notice_reads (user_id)")

        conn.commit()
        conn.close()
        print("Smart features migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    upgrade()
