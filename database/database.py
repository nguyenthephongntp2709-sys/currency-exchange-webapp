import sqlite3
from datetime import datetime

DB_NAME = "exchange.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Trả về kết quả dạng dict/key-value
    return conn

def init_db():
    """Khởi tạo bảng cơ sở dữ liệu."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Bảng lưu lịch sử các lần người dùng quy đổi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_currency TEXT NOT NULL,
            to_currency TEXT NOT NULL,
            amount REAL NOT NULL,
            result REAL NOT NULL,
            rate REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. Bảng lưu lịch sử biến động tỷ giá để vẽ biểu đồ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rate_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT NOT NULL,
            rate REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def save_conversion(from_curr, to_curr, amount, result, rate):
    """Lưu một bản ghi quy đổi mới."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversion_history (from_currency, to_currency, amount, result, rate, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (from_curr.upper(), to_curr.upper(), amount, result, rate, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_all_conversions(limit=50):
    """Đọc danh sách lịch sử quy đổi gần nhất."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversion_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_rate_history(pair="USD/VND", limit=7):
    """Lấy dữ liệu tỷ giá theo ngày để đưa vào biểu đồ."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, rate FROM exchange_rate_history 
        WHERE pair = ? 
        ORDER BY date ASC LIMIT ?
    """, (pair.upper(), limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]