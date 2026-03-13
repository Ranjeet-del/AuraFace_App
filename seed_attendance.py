import sqlite3

def seed():
    conn = sqlite3.connect("attendance.db") # Main db is attendance.db
    cur = conn.cursor()
    
    # Movies (Using standard ISO 8601 formatting for datetime which SQLite/SQLAlchemy prefers)
    cur.execute("""
    INSERT INTO movie_events (title, description, venue, show_time, poster_url, status) 
    VALUES ('Inception', 'A thief steals corporate secrets through dream-sharing technology.', 'Campus Auditorium', '2026-03-10 18:00:00.000', '', 'UPCOMING')
    """)
    cur.execute("""
    INSERT INTO movie_events (title, description, venue, show_time, poster_url, status) 
    VALUES ('Interstellar', 'Explorers travel through a wormhole in space.', 'Main Ground Open Air Theater', '2026-03-12 19:30:00.000', '', 'UPCOMING')
    """)
    
    # Sports
    cur.execute("""
    INSERT INTO sports_tournaments (name, sport_type, start_date, end_date, status) 
    VALUES ('Spring Bash 2026', 'Cricket', '2026-03-15', '2026-03-20', 'UPCOMING')
    """)
    
    # match times need to be compatible with SQLAlchemy
    cur.execute("""
    INSERT INTO sports_matches (tournament_id, team_a, team_b, match_time, venue, status) 
    VALUES (1, 'CSE 3rd Year', 'ECE 4th Year', '2026-03-15 10:00:00.000', 'Main Ground', 'SCHEDULED')
    """)
    
    cur.execute("""
    INSERT INTO sports_matches (tournament_id, team_a, team_b, match_time, venue, status) 
    VALUES (1, 'MECH 2nd Year', 'CIVIL 2nd Year', '2026-03-16 14:00:00.000', 'Main Ground', 'SCHEDULED')
    """)
    
    conn.commit()
    conn.close()
    print("Seeded attendance.db.")

if __name__ == "__main__":
    seed()
