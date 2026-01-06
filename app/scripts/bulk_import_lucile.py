import sqlite3
from datetime import datetime

DB_PATH = "passbook.db"
NOW = datetime.now().isoformat()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ================= SCHEMA (SAFE) =================

cur.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    amount REAL,
    entry_type TEXT,
    category TEXT,
    date TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY,
    note TEXT
)
""")

# ================= RESET DATA =================
print("⚠️ Clearing existing data...")
cur.execute("DELETE FROM entries")
cur.execute("DELETE FROM schedule")
conn.commit()

# ================= HELPER =================

def add(title, amount, entry_type, category=None, date=NOW): # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    cur.execute(
        """
        INSERT INTO entries (title, amount, entry_type, category, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, amount, entry_type, category, date), # pyright: ignore[reportUnknownArgumentType]
    )

# ================= SCHEDULE =================

schedule_text = """Scheduled Maintenance Records

Oil changed at 39692km – 07/07/25
Battery changed – 04/11/2022
Carburetor cleaned – 16/02/24
Cone set changed – 22/04/24
Air filter changed – 20/08/25
Front bearings changed – 11/11/25
Chain & sprocket changed – 14/12/25
Spark plugs changed – 14/12/25
"""

cur.execute(
    "INSERT OR REPLACE INTO schedule (id, note) VALUES (1, ?)",
    (schedule_text,),
)

# ================= MAINTENANCE =================
# Total maintenance = ₹43,414 (stored as one logical record)

add("Total Maintenance Cost", 43414, "maintenance")

# ================= MODIFICATIONS =================

# ---- Accessories ----
accessories = [
    ("LED Strip", 120),
    ("Universal Mobile Mount", 131),
    ("Duplicate key (RE lookalike)", 150),
    ("Horn Harness", 199),
    ("LED Strip", 373),
    ("Flip Key", 440),
    ("UNO Minda D95 Horn", 489),
    ("Simtac LED indicator bulbs", 695),
    ("RE Original Rear Indicators", 750),
    ("Mobile Holder", 900),
    ("Mobile Holder", 1200),
    ("BS Handlebar (fat boy)", 1200),
    ("BS Handlebar (wide grip)", 1200),
    ("Simtac Mobile charger", 1349),
    ("HJG Fog Lights (Small) [1 working]", 1400),
    ("Fog Light Wiring Harness", 1800),
    ("Backrest with carrier", 2000),
    ("HJG Fog Lights (Big)", 2200),
    ("Led Headlight", 3000),
    ("Carbon Racing windshield", 3000),
    ("RE Original Octagon Leg guard", 3200),
    ("HJG Fog Lights (9 Led)", 4850),
]

# ---- Brakes & Clutch ----
brakes_clutch = [
    ("RE Front brake master cylinder cover", 800),
    ("RE Oil Filler Cap", 675),
    ("RE Black brake lever", 160),
    ("RE Black clutch lever", 120),
    ("Clutch cable x2", 360),
    ("Throttle cable", 240),
]

# ---- Tyres ----
tyres = [
    ("MRF Nylon Zapper rear tyre", 3200),
    ("CEAT Grippy XL front tyre", 2000),
    ("CEAT Grippy XL rear tyre", 2500),
]

# ---- Essential Components ----
essentials = [
    ("Cone set", 1100),
    ("Rear piston major kit", 1074),
    ("Amaron battery", 1700),
    ("Front wheel bearings", 460),
    ("Rolon chain & sprocket", 2210),
    ("Iridium spark plugs", 1786),
    ("Tail light", 1895),
    ("Rear lights wiring", 145),
]

# ---- Luggage ----
luggage = [
    ("Guardian Gears tank bag", 3999),
    ("Guardian Gears tail bag", 1923),
    ("Hydration backpack", 933),
]

# ---- Aesthetic ----
aesthetic = [
    ("Black repaint", 10000),
    ("Teflon coating", 885),
]

# ================= INSERT MODS =================

def insert_group(items, category): # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
    for title, amount in items:    # pyright: ignore[reportUnknownVariableType, reportMissingParameterType, reportUnknownParameterType]
        add(title, amount, "modification", category)  #pyright: ignore[reportUnknownArgumentType, reportMissingParameterType, reportUnknownParameterType]

insert_group(accessories, "Accessories")
insert_group(brakes_clutch, "Brakes & Clutch")
insert_group(tyres, "Tyres")
insert_group(essentials, "Essential Components")
insert_group(luggage, "Luggage")
insert_group(aesthetic, "Aesthetic")

# ================= DONE =================

conn.commit()
conn.close()

print("✅ Lucile data imported cleanly")
print("Maintenance: ₹43,414")
print("Modifications: ₹69,488")
print("Grand Total: ₹1,12,902")
