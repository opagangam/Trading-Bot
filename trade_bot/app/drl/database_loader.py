import sqlite3
import pandas as pd

def load_training_data(db_path="trades.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM trade_logs ORDER BY timestamp ASC", conn)
    conn.close()
    return df
