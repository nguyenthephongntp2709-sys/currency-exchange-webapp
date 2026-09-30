from flask import Blueprint, render_template
from services.exchange_api import get_rate
import requests

currency_bp = Blueprint("currency", __name__)


@currency_bp.route("/")
def index():
    try:
        data = get_rate("USD", "VND")

        return render_template(
            "index.html",
            rate=data["rate"],
            date=data["date"],
            error=None
        )

    except requests.RequestException:
        return render_template(
            "index.html",
            rate=None,
            date=None,
            error="Không thể lấy dữ liệu tỷ giá. Vui lòng thử lại sau."
        )