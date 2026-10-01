from flask import Blueprint, render_template, request
from services.vietcombank_service import convert_vcb, get_vcb_rates
from services.exchange_api import get_rate, get_currencies, convert_currency
from database.database import save_conversion
import requests


currency_bp = Blueprint("currency", __name__)


@currency_bp.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    rate = None
    date = None
    currencies = []

    # Giữ lại dữ liệu người dùng đã chọn
    selected_amount = ""
    selected_from = "USD"
    selected_to = "VND"
    selected_source = "frankfurter"
    selected_rate_type = "transfer"

    # =========================
    # LẤY DANH SÁCH TIỀN TỆ
    # =========================
    try:
        currencies = get_currencies()

    except requests.RequestException:
        error = "Không thể lấy danh sách tiền tệ."

    # =========================
    # GET - LẦN ĐẦU MỞ TRANG
    # =========================
    if request.method == "GET":
        try:
            data = get_rate("USD", "VND")

            rate = data["rate"]
            date = data.get("date")

        except requests.RequestException:
            error = "Không thể lấy dữ liệu tỷ giá."

    # =========================
    # POST - NGƯỜI DÙNG QUY ĐỔI
    # =========================
    if request.method == "POST":
        try:
            selected_amount = request.form.get("amount", "")
            selected_from = request.form.get("from_currency", "USD")
            selected_to = request.form.get("to_currency", "VND")
            selected_source = request.form.get(
                "source",
                "frankfurter"
            )
            selected_rate_type = request.form.get(
                "rate_type",
                "transfer"
            )

            amount = float(selected_amount)

            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0.")

            # =========================
            # VIETCOMBANK
            # =========================
            if selected_source == "vietcombank":

                result = convert_vcb(
                    amount,
                    selected_from,
                    selected_to,
                    selected_rate_type
                )

            # =========================
            # FRANKFURTER
            # =========================
            else:

                result = convert_currency(
                    amount,
                    selected_from,
                    selected_to
                )

            # Lấy tỷ giá và ngày để hiển thị
            rate = result["rate"]
            date = result.get("date")

            # =========================
            # LƯU DATABASE
            # =========================
            save_conversion(
                from_curr=result["from_currency"],
                to_curr=result["to_currency"],
                amount=result["amount"],
                result=result["result"],
                rate=result["rate"]
            )

        except ValueError as e:
            error = str(e)

        except requests.RequestException:
            error = "Không thể kết nối tới dịch vụ tỷ giá."

        except Exception as e:
            error = f"Có lỗi xảy ra: {str(e)}"

    # =========================
    # TRẢ VỀ GIAO DIỆN
    # =========================
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