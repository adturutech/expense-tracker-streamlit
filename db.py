import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from zoneinfo import ZoneInfo



DB_PATH = "data/expenses.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL,
      amount REAL NOT NULL,
      category TEXT NOT NULL,
      type TEXT CHECK(type IN ('income','expense')) NOT NULL,
      description TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def get_wib_time():
    return datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")

def insert_transaction(date: str, amount: float, category: str, ttype: str, description: str=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO transactions (date, amount, category, type, description, created_at)
      VALUES (?, ?, ?, ?, ?, ?)
    """, (date, amount, category, ttype, description, get_wib_time()))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def fetch_transactions(limit: int=100, start_date: Optional[str]=None, end_date: Optional[str]=None, category: Optional[str]=None) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    query = "SELECT * FROM transactions"
    clauses = []
    params = []

    if start_date:
        clauses.append("date >= ?")
        params.append(start_date)
    if end_date:
        clauses.append("date <= ?")
        params.append(end_date)
    if category and category.lower() != "all":
        clauses.append("category = ?")
        params.append(category)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, tuple(params))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_transaction(tx_id: int) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_transaction(tx_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()

def update_transaction(tx_id: int, date: str, amount: float, category: str, ttype: str, description: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      UPDATE transactions
      SET date=?, amount=?, category=?, type=?, description=?
      WHERE id=?
    """, (date, amount, category, ttype, description, tx_id))
    conn.commit()
    conn.close()

def list_categories(limit:int=100) -> List[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM transactions ORDER BY category LIMIT ?", (limit,))
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows
