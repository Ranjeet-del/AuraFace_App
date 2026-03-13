import sqlite3
import sys

def migrate():
    db_paths = ["auraface.db", "attendance.db"]
    for path in db_paths:
        try:
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS movie_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR NOT NULL,
                description VARCHAR,
                poster_url VARCHAR,
                trailer_url VARCHAR,
                show_time DATETIME NOT NULL,
                venue VARCHAR NOT NULL,
                duration_mins INTEGER DEFAULT 120,
                total_seats INTEGER DEFAULT 100,
                available_seats INTEGER DEFAULT 100,
                ticket_price FLOAT DEFAULT 0.0,
                status VARCHAR DEFAULT 'UPCOMING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS movie_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER REFERENCES movie_events(id),
                student_id INTEGER REFERENCES students(id),
                seats_booked INTEGER DEFAULT 1,
                booking_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR DEFAULT 'CONFIRMED'
            )
            """)
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sports_tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL,
                sport_type VARCHAR NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                registration_deadline DATE,
                status VARCHAR DEFAULT 'UPCOMING',
                banner_url VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sports_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER REFERENCES sports_tournaments(id),
                team_a VARCHAR NOT NULL,
                team_b VARCHAR NOT NULL,
                match_time DATETIME NOT NULL,
                venue VARCHAR NOT NULL,
                status VARCHAR DEFAULT 'SCHEDULED',
                score_team_a VARCHAR,
                score_team_b VARCHAR,
                winner VARCHAR,
                is_live BOOLEAN DEFAULT 0
            )
            """)
            
            conn.commit()
            print(f"Successfully migrated {path}")
            conn.close()
            
        except Exception as e:
            print(f"Error on {path}: {e}")

if __name__ == "__main__":
    migrate()
