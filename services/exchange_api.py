import requests

BASE_URL = "https://api.frankfurter.dev/v2"


def get_rate(from_currency, to_currency):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    # Nếu đổi cùng một loại tiền
    if from_currency == to_currency:
        return {
            "date": None,
            "base": from_currency,
            "quote": to_currency,
            "rate": 1
        }

    url = f"{BASE_URL}/rate/{from_currency}/{to_currency}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()

def get_currencies():
    url = f"{BASE_URL}/currencies"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()


def convert_currency(amount, from_currency, to_currency):
    data = get_rate(from_currency, to_currency)

    rate = data["rate"]
    result = amount * rate

    return {
        "amount": amount,
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "rate": rate,
        "result": result,
        "date": data.get("date"),
        "source": "frankfurter"
    }


if __name__ == "__main__":
    data = get_currencies()     
    print(data)