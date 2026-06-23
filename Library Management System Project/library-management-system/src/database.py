import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'library.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'sql', 'schema.sql')

def get_connection():
    """Veritabanı bağlantısı döndürür (row_factory = sqlite3.Row)"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Şemayı çalıştırır, tabloları ve trigger'ları oluşturur."""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema dosyası bulunamadı: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    with get_connection() as conn:
        conn.executescript(schema_sql)
        conn.commit()