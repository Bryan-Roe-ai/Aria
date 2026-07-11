import pyodbc

conn_str
=
(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=aria-24563.database.windows.net,1433;"
    "DATABASE=Database;"  # replace
if needed
    "UID=<username>;"
    "PWD=<password>;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

with pyodbc.connect
(conn_str) as
conn:
cursor = conn.cursor
()
    cursor.
execute("SELECT 1 AS ok"
)
print(cursor.fetchone())
