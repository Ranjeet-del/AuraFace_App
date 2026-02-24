import sqlite3
import os

db_path = os.path.join(os.getcwd(), "attendance.db")
print(f"Connecting to {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create SentMessage table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            content TEXT,
            target_group TEXT,
            created_at DATETIME,
            FOREIGN KEY (sender_id) REFERENCES users(id)
        )
    """)
    print("Created sent_messages table.")
    
    # Add sent_message_id column to notifications
    try:
        cursor.execute("ALTER TABLE notifications ADD COLUMN sent_message_id INTEGER")
        print("Added sent_message_id column.")
    except sqlite3.OperationalError:
        print("Column sent_message_id likely already exists.")
        
    conn.commit()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
