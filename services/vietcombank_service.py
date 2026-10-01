import requests
import xml.etree.ElementTree as ET

VCB_URL = (
    "https://portal.vietcombank.com.vn/"
    "Usercontrols/TVPortal.TyGia/pXML.aspx?b=10"
)

def parse_rate(value):
    if value is None or value == "-":
        return None

    return float(value.replace(",", ""))


def get_vcb_rates():
    response = requests.get(VCB_URL, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    rates = []

    for item in root.findall("Exrate"):
        rates.append({
            "currency_code": item.attrib.get("CurrencyCode"),
            "currency_name": item.attrib.get(
                "CurrencyName", ""
            ).strip(),

            "buy": parse_rate(
                item.attrib.get("Buy")
            ),

            "transfer": parse_rate(
                item.attrib.get("Transfer")
            ),

            "sell": parse_rate(
                item.attrib.get("Sell")
            )
        })

    return rates


def get_vcb_rate(currency_code):
    currency_code = currency_code.upper()

    rates = get_vcb_rates()

    for item in rates:
        if item["currency_code"] == currency_code:
            return item

    return None

def convert_vcb(amount, from_currency, to_currency, rate_type="transfer"):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if amount <= 0:
        raise ValueError("Số tiền phải lớn hơn 0.")

    # Cùng loại tiền
    if from_currency == to_currency:
        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": 1,
            "rate_type": "same_currency",
            "result": amount
        }

    # Ngoại tệ -> VND
    # Ngân hàng MUA ngoại tệ của khách hàng
    if to_currency == "VND":
        data = get_vcb_rate(from_currency)

        if data is None:
            raise ValueError("Vietcombank không hỗ trợ ngoại tệ này.")

        if rate_type == "cash":
            rate = data["buy"]
        else:
            rate = data["transfer"]

        if rate is None:
            raise ValueError("Không có tỷ giá mua cho ngoại tệ này.")

        result = amount * rate

    # VND -> Ngoại tệ
    # Khách hàng MUA ngoại tệ từ ngân hàng
    elif from_currency == "VND":
        data = get_vcb_rate(to_currency)

        if data is None:
            raise ValueError("Vietcombank không hỗ trợ ngoại tệ này.")

        rate = data["sell"]

        if rate is None:
            raise ValueError("Không có tỷ giá bán cho ngoại tệ này.")

        result = amount / rate
        rate_type = "sell"

    else:
        raise ValueError(
            "Vietcombank chỉ hỗ trợ quy đổi giữa VND và ngoại tệ."
        )

    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "rate": rate,
        "rate_type": rate_type,
        "result": result,
        "source": "vietcombank"
    }

if __name__ == "__main__":
    print("USD -> VND:")
    print(
        convert_vcb(
            100,
            "USD",
            "VND",
            "transfer"
        )
    )

    print()

    print("VND -> USD:")
    print(
        convert_vcb(
            2616000,
            "VND",
            "USD"
        )
    )