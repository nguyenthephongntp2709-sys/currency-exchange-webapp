from flask import Blueprint, render_template, request
from services.exchange_api import get_rate, get_currencies, convert_currency
from services.vietcombank_service import convert_vcb
import requests

currency_bp = Blueprint("currency", __name__)


@currency_bp.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    rate = None
    date = None
    currencies = []

    # Lấy danh sách tiền tệ
    try:
        currencies = get_currencies()

    except requests.RequestException:
        error = "Không thể lấy danh sách tiền tệ."

    # Lấy tỷ giá USD -> VND mặc định
    try:
        data = get_rate("USD", "VND")
        rate = data["rate"]
        date = data.get("date")

    except requests.RequestException:
        error = "Không thể lấy dữ liệu tỷ giá."

    # Khi người dùng nhấn nút Quy đổi
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            from_currency = request.form["from_currency"]
            to_currency = request.form["to_currency"]

            source = request.form.get("source", "frankfurter")

            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0.")

            if source == "vietcombank":

                rate_type = request.form.get(
                    "rate_type",
                    "transfer"
                )

                result = convert_vcb(
                    amount,
                    from_currency,
                    to_currency,
                    rate_type
                )

            else:

                result = convert_currency(
                    amount,
                    from_currency,
                    to_currency
                )

        except ValueError as e:
            error = str(e)

        except requests.RequestException:
            error = "Không thể kết nối tới dịch vụ tỷ giá."

    return render_template(
        "index.html",
        rate=rate,
        date=date,
        currencies=currencies,
        result=result,
        error=error
    )