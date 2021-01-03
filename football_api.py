import json

import requests

url = "https://v3.football.api-sports.io/fixtures/league/524/last/10"

payload = {}
headers = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': '5453c6e17010446f88dab41a62c97a53'
}

response = requests.request("GET", url, headers=headers, data=payload)
# print(response.text)

obj = json.loads(response.text)
# print(obj)

fixtures = obj['api']['fixtures']

for fixture in fixtures:
    print(fixture)
