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
obj = fetch_data_from_file(file_name='../json/leagues_pd.json')
# obj = fetch_data_from_api(url='https://v3.football.api-sports.io/leagues?id=39')


############################ FROM HERE IS DIFFERENT PER SCRIPT #########################################################
response = obj['response']

for json_obj in response:
    league = json_obj["league"]
    country = json_obj["country"]
    seasons = json_obj["seasons"]
    league_name = league['name']
    print(league_name)

    # create document from team
    doc_ref = db.collection(u'leagues').document(f'{league_name}')
    doc_ref.set({f'league': league}, merge=True)
    doc_ref.set({f'country': country}, merge=True)
    doc_ref.set({f'seasons': seasons}, merge=True)
