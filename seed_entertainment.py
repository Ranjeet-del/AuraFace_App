import sqlite3

def seed():
    conn = sqlite3.connect("auraface.db")
    cur = conn.cursor()
    
    # Movies
    cur.execute("""
    INSERT INTO movie_events (title, description, venue, show_time, poster_url) 
    VALUES ('Inception', 'A thief steals corporate secrets through dream-sharing technology.', 'Campus Auditorium', '2026-03-10 18:00:00', '')
    """)
    cur.execute("""
    INSERT INTO movie_events (title, description, venue, show_time, poster_url) 
    VALUES ('Interstellar', 'Explorers travel through a wormhole in space.', 'Main Ground Open Air Theater', '2026-03-12 19:30:00', '')
    """)
    
    # Sports
    cur.execute("""
    INSERT INTO sports_tournaments (name, sport_type, start_date, end_date) 
    VALUES ('Spring Bash 2026', 'Cricket', '2026-03-15', '2026-03-20')
    """)
    cur.execute("""
    INSERT INTO sports_matches (tournament_id, team_a, team_b, match_time, venue) 
    VALUES (1, 'CSE 3rd Year', 'ECE 4th Year', '2026-03-15 10:00:00', 'Main Ground')
    """)
    
    conn.commit()
    conn.close()
    print("Seeded database.")

if __name__ == "__main__":
    seed()
