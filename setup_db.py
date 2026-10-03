"""
Run this ONCE on your own computer to create the tables in your Aiven MySQL database.
    python setup_db.py
It will ask for the connection details shown on your Aiven service page.

Same schema as final_database_file.sql, but table names are lowercase because
app.py uses lowercase names and MySQL on Linux (Aiven) is case-sensitive.
"""
import mysql.connector

host = input("Host (e.g. mysql-xxxx.aivencloud.com): ").strip()
port = int(input("Port (e.g. 12345): ").strip())
user = input("User [avnadmin]: ").strip() or "avnadmin"
password = input("Password: ").strip()
database = input("Database [defaultdb]: ").strip() or "defaultdb"

conn = mysql.connector.connect(host=host, port=port, user=user,
                               password=password, database=database)
cur = conn.cursor()

with open(__file__.replace("setup_db.py", "aiven_database.sql"), encoding="utf-8") as f:
    # drop comment lines, then run each statement
    sql = "".join(line for line in f if not line.strip().startswith("--"))

for statement in sql.split(";"):
    statement = statement.strip()
    if statement:
        cur.execute(statement)
        if cur.with_rows:
            cur.fetchall()

conn.commit()
cur.execute("SHOW TABLES")
print("Done. Tables:", [t[0] for t in cur.fetchall()])
cur.execute("SELECT Doctor_ID, Name FROM doctor")
print("Doctors:", cur.fetchall())
cur.close()
conn.close()
