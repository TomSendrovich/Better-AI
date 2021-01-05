import json

import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import firestore


def connect_db():
    # Use a service account
    cred = credentials.Certificate('../better-gsts-60715c303402.json')
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    return db


def fetch_data_from_file(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def fetch_data_from_api(url):
    payload = {}
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '5453c6e17010446f88dab41a62c97a53'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    obj = json.loads(response.text)

    return obj


############################ CONNECT FIRESTORE DB ######################################################################
db = connect_db()

############################ FETCH DATA USING API OR JSON FILE #########################################################
obj = fetch_data_from_file(file_name='../json/fixtures_2020_pl.json')
# obj = fetch_data_from_api(url='https://v3.football.api-sports.io/fixtures?season=2020&league=39')


############################ FROM HERE IS DIFFERENT PER SCRIPT #########################################################
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
