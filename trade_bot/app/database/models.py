import sqlite3

DB_FILE = "database/trades.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                price REAL,
                sentiment_score REAL,
                price_change_pct REAL,
                decision TEXT
            )
        """)
        conn.commit()

def log_trade(ticker, price, sentiment_score, price_change_pct, decision):
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trade_logs (ticker, price, sentiment_score, price_change_pct, decision)
            VALUES (?, ?, ?, ?, ?)
        """, (ticker, price, sentiment_score, price_change_pct, decision))
        conn.commit()
