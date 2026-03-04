import sqlite3
import os

db_path = os.path.join("app", "data", "bot.db")
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}. No migration needed.")
else:
    conn = sqlite3.connect(db_path)
    try:
        try:
            conn.execute("ALTER TABLE users ADD COLUMN show_in_top BOOLEAN DEFAULT 0;")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        
        conn.execute("UPDATE users SET show_in_top = 0;")
        conn.commit()
        print("Successfully updated database: show_in_top is now 0 (False) for everyone.")
    finally:
        conn.close()
