import requests


url = "https://api.frankfurter.dev/v2/rate/usd/vnd"

response = requests.get(url)

print(response.status_code)
print(response.json())