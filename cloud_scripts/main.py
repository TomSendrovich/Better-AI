import json

import google.cloud.firestore
import requests


def fetch_data_from_api(url):
    payload = {}
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '5453c6e17010446f88dab41a62c97a53'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    obj = json.loads(response.text)

    return obj


def update_fixtures_pl(self):
    league_id = 39
    update_fixtures(league_id)
    return f'Done, league_id={league_id}'


def update_fixtures_pd(self):
    league_id = 140
    update_fixtures(league_id)
    return f'Done, league_id={league_id}'


def update_fixtures(league_id):
    db = google.cloud.firestore.Client()

    url = f'https://v3.football.api-sports.io/fixtures?season=2020&league={league_id}&last=10'

    obj = fetch_data_from_api(url=url)

    response = obj['response']

    for json_obj in response:
        fixture_id = json_obj["fixture"]["id"]
        fixture_date = (json_obj["fixture"]["date"]).split(':')[0]
        print(f'{fixture_date}-{fixture_id}')

        doc_ref = db.collection(u'fixtures').document(f'{fixture_date}-{fixture_id}')

        fixture = json_obj["fixture"]
        league = json_obj["league"]
        teams = json_obj["teams"]
        goals = json_obj["goals"]
        score = json_obj["score"]

        doc_ref.set({f'fixture': fixture}, merge=True)
        doc_ref.set({f'league': league}, merge=True)
        doc_ref.set({f'teams': teams}, merge=True)
        doc_ref.set({f'goals': goals}, merge=True)
        doc_ref.set({f'score': score}, merge=True)
