# app/scripts/check_missing_mods.py
import sqlite3

conn = sqlite3.connect("passbook.db")
cur = conn.cursor()

cur.execute("""
SELECT title, amount, category
FROM entries
WHERE entry_type='modification'
ORDER BY category
""")

rows = cur.fetchall()
total = 0

for r in rows:
    print(r)
    total += r[1]

print("\nCALCULATED TOTAL:", total)
conn.close()
