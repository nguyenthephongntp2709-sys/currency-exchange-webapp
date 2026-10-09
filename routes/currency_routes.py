import math
import xml.etree.ElementTree as ET

import requests
from flask import Blueprint, render_template, request

from services.exchange_api import get_currencies, convert_currency
from services.vietcombank_service import get_vcb_rates, convert_vcb
from database.database import save_conversion


currency_bp = Blueprint("currency", __name__)


def has_valid_rate(value):
    """Tỷ giá hợp lệ phải là số hữu hạn và lớn hơn 0."""
    try:
        number = float(value)
        return math.isfinite(number) and number > 0
    except (TypeError, ValueError):
        return False


@currency_bp.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    rate = None
    date = None

    currencies = []
    vcb_currencies = []

    selected_amount = ""
    selected_from = "USD"
    selected_to = "VND"
    selected_source = "frankfurter"
    selected_rate_type = "transfer"

    # Lấy lựa chọn trước khi kiểm tra dữ liệu,
    # để vẫn giữ form kể cả khi quy đổi bị lỗi.
    if request.method == "POST":
        selected_amount = request.form.get("amount", "")
        selected_from = request.form.get(
            "from_currency", "USD"
        ).upper()
        selected_to = request.form.get(
            "to_currency", "VND"
        ).upper()
        selected_source = request.form.get(
            "source", "frankfurter"
        )
        selected_rate_type = request.form.get(
            "rate_type", "transfer"
        )

    # Danh sách tiền riêng của Frankfurter.
    try:
        currencies = get_currencies()
    except (requests.RequestException, ValueError):
        currencies = []

    # Danh sách tiền riêng của Vietcombank.
    # cash ứng với trường buy trong dữ liệu ngân hàng.
    try:
        for item in get_vcb_rates():
            code = (item.get("currency_code") or "").strip().upper()

            if not code or code == "VND":
                continue

            currency = {
                "iso_code": code,
                "name": item.get("currency_name") or code,
                "cash": has_valid_rate(item.get("buy")),
                "transfer": has_valid_rate(item.get("transfer")),
                "sell": has_valid_rate(item.get("sell")),
            }

            # Bỏ đồng tiền không có tỷ giá ở cả ba nghiệp vụ.
            if currency["cash"] or currency["transfer"] or currency["sell"]:
                vcb_currencies.append(currency)

        vcb_currencies.sort(key=lambda item: item["iso_code"])

    except (
        requests.RequestException,
        ET.ParseError,
        ValueError,
        TypeError,
    ):
        vcb_currencies = []

    if request.method == "POST":
        try:
            try:
                amount = float(selected_amount)
            except (TypeError, ValueError):
                raise ValueError("Vui lòng nhập số tiền hợp lệ.")

            if not math.isfinite(amount) or amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0.")

            if selected_source == "vietcombank":
                if not vcb_currencies:
                    raise ValueError(
                        "Không tải được tỷ giá Vietcombank. "
                        "Vui lòng thử lại hoặc chọn Frankfurter."
                    )

                supported = {
                    item["iso_code"]: item
                    for item in vcb_currencies
                }

                # VND -> ngoại tệ: chỉ dùng giá bán.
                if selected_from == "VND" and selected_to != "VND":
                    selected_rate_type = "sell"
                    currency = supported.get(selected_to)

                    if not currency or not currency["sell"]:
                        raise ValueError(
                            "Ngoại tệ này không có tỷ giá bán "
                            "tại Vietcombank."
                        )

                # Ngoại tệ -> VND: mua tiền mặt hoặc chuyển khoản.
                elif selected_from != "VND" and selected_to == "VND":
                    if selected_rate_type not in ("cash", "transfer"):
                        raise ValueError(
                            "Vui lòng chọn mua chuyển khoản "
                            "hoặc mua tiền mặt."
                        )

                    currency = supported.get(selected_from)

                    if not currency or not currency[selected_rate_type]:
                        raise ValueError(
                            "Ngoại tệ này không có tỷ giá "
                            "cho loại giao dịch đã chọn."
                        )

                else:
                    raise ValueError(
                        "Vietcombank chỉ hỗ trợ quy đổi "
                        "giữa VND và ngoại tệ."
                    )

                result = convert_vcb(
                    amount,
                    selected_from,
                    selected_to,
                    selected_rate_type,
                )

            elif selected_source == "frankfurter":
                supported_codes = {
                    item["iso_code"] for item in currencies
                }

                if (
                    selected_from not in supported_codes
                    or selected_to not in supported_codes
                ):
                    raise ValueError(
                        "Không có tiền tệ đã chọn trong "
                        "danh sách Frankfurter."
                    )

                result = convert_currency(
                    amount,
                    selected_from,
                    selected_to,
                )

            else:
                raise ValueError("Nguồn tỷ giá không hợp lệ.")

            rate = result["rate"]
            date = result.get("date")

            save_conversion(
                from_curr=result["from_currency"],
                to_curr=result["to_currency"],
                amount=result["amount"],
                result=result["result"],
                rate=result["rate"],
            )

        except ValueError as exc:
            error = str(exc)

        except requests.RequestException:
            error = "Không thể kết nối tới dịch vụ tỷ giá."

        except Exception as exc:
            error = f"Có lỗi xảy ra: {exc}"

    return render_template(
        "index.html",
        currencies=currencies,
        vcb_currencies=vcb_currencies,
        rate=rate,
        date=date,
        result=result,
        error=error,
        selected_amount=selected_amount,
        selected_from=selected_from,
        selected_to=selected_to,
        selected_source=selected_source,
        selected_rate_type=selected_rate_type,
    )