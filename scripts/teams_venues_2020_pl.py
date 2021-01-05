import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import firestore

import json


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
obj = fetch_data_from_file(file_name='../json/teams_venues_2020_pl.json')
# obj = fetch_data_from_api(url='https://v3.football.api-sports.io/teams?league=39&season=2020')


############################ FROM HERE IS DIFFERENT PER SCRIPT #########################################################
response = obj['response']

for json_obj in response:
    team = json_obj["team"]
    team_name = team['name']
    print(team_name)

    # create document from team
    doc_ref = db.collection(u'teams').document(f'{team_name}')
    doc_ref.set(team)

    venue = json_obj["venue"]
    venue_name = venue['name']

    # create document from venue
    doc_ref = db.collection(u'venues').document(f'{venue_name}')
    doc_ref.set(venue)
