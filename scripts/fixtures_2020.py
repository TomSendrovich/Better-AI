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


def update_fixtures(request_args):
    # check arg 'league_id'. mandatory
    if request_args and 'league_id' in request_args:
        league_id = request_args['league_id']
    else:
        msg = 'Error: league_id parameter is missing'
        print(msg)
        return msg

    # check args 'from' and 'to'. no mandatory
    if request_args and 'from' in request_args and 'to' in request_args:
        param_from = request_args['from']
        param_to = request_args['to']
        date_filter = True
    else:
        date_filter = False

    # build url from request args
    if date_filter:
        url = f'https://v3.football.api-sports.io/fixtures?season=2020&league={league_id}&from={param_from}&to={param_to}'
    else:
        url = f'https://v3.football.api-sports.io/fixtures?season=2020&league={league_id}&last=10'

    # connect db
    db = connect_db()
    batch = db.batch()

    # get json response
    # obj = fetch_data_from_api(url=url)
    obj = fetch_data_from_file(file_name='../json/fixtures_2020_pl.json')
    response = obj['response']
    results_count = obj['results']

    count = 0

    for json_obj in response:
        count = count + 1

        fixture_id = json_obj["fixture"]["id"]
        fixture_date = (json_obj["fixture"]["date"]).split(':')[0]

        print(f'{fixture_date}-{fixture_id}, {count / results_count * 100:.2f}%')

        doc_ref = db.collection(u'fixtures').document(f'{fixture_date}-{fixture_id}')

        fixture = json_obj["fixture"]
        league = json_obj["league"]
        teams = json_obj["teams"]
        goals = json_obj["goals"]
        score = json_obj["score"]

        # each batch.set is 1 operation
        batch.set(doc_ref, {f'fixture': fixture}, merge=True)
        batch.set(doc_ref, {f'league': league}, merge=True)
        batch.set(doc_ref, {f'teams': teams}, merge=True)
        batch.set(doc_ref, {f'goals': goals}, merge=True)
        batch.set(doc_ref, {f'score': score}, merge=True)

        # commit every X documents for better performance (max is 500 operations per batch)
        if count % 50 == 0:
            batch.commit()

    batch.commit()  # commit the rest of oeprations

    # print a summary line
    if date_filter:
        res = f'Success for {count} fixtures: league_id={league_id}, from={param_from}, to={param_to}'
    else:
        res = f'Success for {count} fixtures: league_id={league_id}'
    print(res)
    return res


args = {'league_id': 39, 'from': '2021-01-04', 'to': '2021-01-07'}
update_fixtures(args)
