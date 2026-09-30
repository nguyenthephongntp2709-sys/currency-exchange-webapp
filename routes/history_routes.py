from flask import Blueprint, render_template, jsonify
from database.database import get_all_conversions, get_rate_history

# Tạo Blueprint riêng cho lịch sử
history_bp = Blueprint("history_bp", __name__)

@history_bp.route("/history")
def history_page():
    # Lấy toàn bộ lịch sử quy đổi để truyền vào HTML
    conversions = get_all_conversions()
    return render_template("history.html", conversions=conversions)

@history_bp.route("/api/rate-history/<path:pair>")
def rate_history_api(pair):
    # API trả dữ liệu JSON cho biểu đồ Chart.js
    data = get_rate_history(pair=pair)
    labels = [row["date"] for row in data]
    rates = [row["rate"] for row in data]
    return jsonify({"labels": labels, "rates": rates})