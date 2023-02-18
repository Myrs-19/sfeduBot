import sqlite3

try:
    conn = sqlite3.connect('../sfeduBot/db.sqlite3')
    cur = conn.cursor()

except:
    conn.close()
    exit(0)