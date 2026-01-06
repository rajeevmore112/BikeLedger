import sqlite3

conn = sqlite3.connect("passbook.db")
cur = conn.cursor()

cur.execute("""
SELECT id, title, amount
FROM entries
WHERE entry_type = 'maintenance'
""")

for row in cur.fetchall():
    print(row)

conn.close()
