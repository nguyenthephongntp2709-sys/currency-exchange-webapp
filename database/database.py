import sqlite3
from datetime import datetime, timedelta
import random

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
    cursor.execute(
        """
        INSERT INTO conversion_history (from_currency, to_currency, amount, result, rate, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            from_curr.upper(),
            to_curr.upper(),
            amount,
            result,
            rate,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def get_all_conversions(limit=50):
    """Đọc danh sách lịch sử quy đổi gần nhất."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM conversion_history ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_rate_history(pair="USD/VND", period="7d"):
    """Lấy dữ liệu tỷ giá theo mốc thời gian: 7d (7 ngày), 1m (1 tháng), 1y (1 năm)."""
    days_map = {"7d": 7, "1m": 30, "1y": 365}
    limit = days_map.get(period, 7)

    conn = get_connection()
    cursor = conn.cursor()

    # Lấy N bản ghi mới nhất, sau đó đảo ngược theo thứ tự thời gian tăng dần để vẽ biểu đồ từ trái qua phải
    cursor.execute(
        """
        SELECT date, rate FROM (
            SELECT date, rate FROM exchange_rate_history 
            WHERE pair = ? 
            ORDER BY date DESC 
            LIMIT ?
        ) ORDER BY date ASC
    """,
        (pair.upper(), limit),
    )

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def seed_rate_history():
    """Tạo dữ liệu tỷ giá giả lập cho 365 ngày gần nhất"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM exchange_rate_history")
    if cursor.fetchone()[0] == 0:
        base_rate = 25400.0
        sample_rates = []
        today = datetime.now()

        # Tạo dữ liệu lùi dần 365 ngày về trước
        for i in range(365, -1, -1):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            # Tỷ giá dao động ngẫu nhiên quanh mức cơ sở
            rate = round(base_rate + random.uniform(-150, 150) + (365 - i) * 1.2, 1)
            sample_rates.append(("USD/VND", rate, date_str))

        cursor.executemany(
            "INSERT INTO exchange_rate_history (pair, rate, date) VALUES (?, ?, ?)",
            sample_rates,
        )
        conn.commit()
    conn.close()
