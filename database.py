import sqlite3

DB_NAME = "welcome_bot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value)
        VALUES ('next_video', '1')
    """)

    conn.commit()
    conn.close()


def get_next_video():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM settings WHERE key = 'next_video'"
    )

    result = cursor.fetchone()
    conn.close()

    return int(result[0]) if result else 1


def set_next_video(video_number):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE settings
        SET value = ?
        WHERE key = 'next_video'
    """, (str(video_number),))

    conn.commit()
    conn.close()