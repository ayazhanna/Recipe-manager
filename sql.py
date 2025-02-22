import sqlite3

conn = sqlite3.connect('weba0.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        hash TEXT
    )
''')

conn.commit()
conn.close()
