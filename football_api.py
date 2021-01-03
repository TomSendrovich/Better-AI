import json

import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import firestore


def connect_db():
    # Use a service account
    cred = credentials.Certificate('better-gsts-60715c303402.json')
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    return db


def fetch_data():
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

    return obj


db = connect_db()
obj = fetch_data()

fixtures = obj['api']['fixtures']

for fixture in fixtures:
    print(fixture)

    # create document (id equals fixture id)
    fixture_id = fixture['fixture_id']
    doc_ref = db.collection(u'fixtures').document(f'{fixture_id}')

    # iterate over fixture keys
    for key in fixture:
        # add key and value to doc (merge=True means the operations don't overwrite existing fields, just simple add)
        doc_ref.set({
            f'{key}': fixture[key],
        }, merge=True)
