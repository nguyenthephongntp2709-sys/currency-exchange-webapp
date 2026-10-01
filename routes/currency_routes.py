from flask import Blueprint, render_template, request
from services.exchange_api import get_rate
from database.database import save_conversion
import requests

currency_bp = Blueprint("currency", __name__)


@currency_bp.route("/", methods=["GET", "POST"])
def index():
    conversion_result = None
    rate = None
    date = None
    error = None

    # Giá trị mặc định khi mới mở trang
    from_curr = "USD"
    to_curr = "VND"
    amount = 1.0

    try:
        if request.method == "POST":
            # 1. Lấy dữ liệu người dùng nhập từ form
            amount = float(request.form.get("amount", 1))
            from_curr = request.form.get("from_currency", "USD")
            to_curr = request.form.get("to_currency", "VND")

            # 2. Gọi API lấy tỷ giá giữa 2 đồng tiền đã chọn
            data = get_rate(from_curr, to_curr)
            rate = data["rate"]
            date = data["date"]

            # 3. Tính toán kết quả quy đổi
            conversion_result = amount * rate

            # 4. Lưu trực tiếp vào SQLite database
            save_conversion(
                from_curr=from_curr,
                to_curr=to_curr,
                amount=amount,
                result=conversion_result,
                rate=rate
            )

        else:
            # Khi người dùng truy cập lần đầu bằng phương thức GET
            data = get_rate("USD", "VND")
            rate = data["rate"]
            date = data["date"]

    except requests.RequestException:
        error = "Không thể lấy dữ liệu tỷ giá. Vui lòng thử lại sau."
    except Exception as e:
        error = f"Có lỗi xảy ra: {str(e)}"

    return render_template(
        "index.html",
        rate=rate,
        date=date,
        result=conversion_result,
        amount=amount,
        from_currency=from_curr,
        to_currency=to_curr,
        error=error
    )