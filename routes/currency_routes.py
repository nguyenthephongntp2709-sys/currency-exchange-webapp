from flask import Blueprint, render_template, request
from services.vietcombank_service import convert_vcb, get_vcb_rates
from database.database import save_conversion
from services.exchange_api import get_rate, get_currencies, convert_currency
import requests

currency_bp = Blueprint("currency", __name__)


@currency_bp.route("/", methods=["GET", "POST"])
def index():
    vcb_currencies = []
    result = None
    error = None
    rate = None
    date = None
    currencies = []

    selected_amount = ""
    selected_from = "USD"
    selected_to = "VND"
    selected_source = "frankfurter"
    selected_rate_type = "transfer"

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
            selected_amount = request.form["amount"]
            selected_from = request.form["from_currency"]
            selected_to = request.form["to_currency"]
            selected_source = request.form.get("source", "frankfurter")
            selected_rate_type = request.form.get("rate_type", "transfer")

            amount = float(selected_amount)
            from_currency = selected_from
            to_currency = selected_to
            source = selected_source

            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0.")

            if source == "vietcombank":

                result = convert_vcb(
                    amount,
                    from_currency,
                    to_currency,
                    selected_rate_type
                )

            else:
                result = convert_currency(
                    amount,
                    from_currency,
                    to_currency
                )

            save_conversion(
                result["from_currency"],
                result["to_currency"],
                result["amount"],
                result["result"],
                result["rate"]
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
        error=error,

        selected_amount=selected_amount,
        selected_from=selected_from,
        selected_to=selected_to,
        selected_source=selected_source,
        selected_rate_type=selected_rate_type
    )