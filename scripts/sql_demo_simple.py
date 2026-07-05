import sqlite3
from pathlib import Path

def main():
    db_path = Path("data_out/qai_local.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT 1")
    val = cur.fetchone()[0]
    print(f"SQL demo query returned: {val}")

if __name__ == "__main__":
    main()
