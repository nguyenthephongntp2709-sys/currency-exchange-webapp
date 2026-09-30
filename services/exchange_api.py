import requests

BASE_URL = "https://api.frankfurter.dev/v2"


def get_rate(from_currency, to_currency):
    url = f"{BASE_URL}/rate/{from_currency}/{to_currency}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    data = get_rate("USD", "VND")
    print(data)