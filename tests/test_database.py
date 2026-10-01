import unittest
import os
import database.database as db

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Đổi tên file DB riêng biệt để test không ảnh hưởng DB thật
        db.DB_NAME = "test_exchange.db"
        db.init_db()

    def tearDown(self):
        # Dọn dẹp file test sau khi chạy xong
        if os.path.exists("test_exchange.db"):
            os.remove("test_exchange.db")

    def test_save_and_get_conversion(self):
        # Test lưu và đọc lại dữ liệu quy đổi
        db.save_conversion("USD", "VND", 100.0, 2591300.0, 25913.0)
        history = db.get_all_conversions(limit=10)
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["from_currency"], "USD")
        self.assertEqual(history[0]["to_currency"], "VND")
        self.assertEqual(history[0]["amount"], 100.0)
        self.assertEqual(history[0]["result"], 2591300.0)

    def test_empty_history(self):
        # Test khi chưa có dữ liệu thì danh sách trả về phải rỗng
        history = db.get_all_conversions()
        self.assertEqual(len(history), 0)

if __name__ == "__main__":
    unittest.main()