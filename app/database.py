import sqlite3
from datetime import datetime
from os import makedirs
from os.path import basename, dirname, exists, join, splitext
from shutil import copy2
from kivy.utils import platform # pyright: ignore[reportMissingTypeStubs]
from kivy.app import App # pyright: ignore[reportMissingTypeStubs]


def get_db_path():
    """
    Returns a writable DB path for both desktop and Android
    """
    if platform == "android":
        return join(App.get_running_app().user_data_dir, "passbook.db") # pyright: ignore[reportUnknownMemberType, reportOptionalMemberAccess, reportUnknownArgumentType]
    return "passbook.db"


def create_backup(db_path, reason="backup"):
    if not exists(db_path):
        return None

    db_dir = dirname(db_path) or "."
    backup_dir = join(db_dir, "backups")
    makedirs(backup_dir, exist_ok=True)

    name, ext = splitext(basename(db_path))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_reason = "".join(ch if ch.isalnum() else "_" for ch in reason).strip("_")
    backup_path = join(backup_dir, f"{name}_{safe_reason}_{timestamp}{ext}")
    copy2(db_path, backup_path)
    return backup_path


class Database:
    def __init__(self):
        self.db_path = get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.ensure_schema()

    def ensure_schema(self):
        cur = self.conn.cursor()

        # --- Core tables ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY,
                note TEXT
            )
        """)

        # --- Schema migration for entries ---
        cur.execute("PRAGMA table_info(entries)")
        cols = [c[1] for c in cur.fetchall()]

        migrations = {
            "title": "ALTER TABLE entries ADD COLUMN title TEXT",
            "amount": "ALTER TABLE entries ADD COLUMN amount REAL",
            "entry_type": "ALTER TABLE entries ADD COLUMN entry_type TEXT",
            "category": "ALTER TABLE entries ADD COLUMN category TEXT",
            "date": "ALTER TABLE entries ADD COLUMN date TEXT",
        }

        for col, sql in migrations.items():
            if col not in cols:
                cur.execute(sql)

        self.conn.commit()
