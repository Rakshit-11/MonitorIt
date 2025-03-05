import sqlite3

conn = sqlite3.connect("activity_log.db")
c = conn.cursor()
c.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 5")
print(c.fetchall())
conn.close()
