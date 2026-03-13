import sqlite3

def add_calendar_events_table():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR NOT NULL,
                date_str VARCHAR NOT NULL,
                event_type VARCHAR NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Successfully added calendar_events table.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_calendar_events_table()
