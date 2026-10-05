from flask import Flask
from routes.currency_routes import currency_bp
from routes.history_routes import history_bp
from database.database import init_db, seed_rate_history 

app = Flask(__name__)

# Tự động tạo file exchange.db và các bảng nếu chưa có
init_db()

# GỌI HÀM NÀY ĐỂ BƠM DỮ LIỆU VÀO DATABASE NẾU DATABASE TRỐNG
seed_rate_history() 

# Đăng ký các Blueprint
app.register_blueprint(currency_bp)
app.register_blueprint(history_bp)

if __name__ == "__main__":
    app.run(debug=True)