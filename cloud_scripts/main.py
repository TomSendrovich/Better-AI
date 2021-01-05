import json

import google.cloud.firestore
import requests
from flask import escape


def fetch_data_from_api(url):
    payload = {}
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '5453c6e17010446f88dab41a62c97a53'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    obj = json.loads(response.text)

    return obj


def update_fixtures(request):
    request_args = request.args

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
    db = google.cloud.firestore.Client()

    # get json response
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

    if date_filter:
        res = f'Success: league_id={league_id}, from={param_from}, to={param_to}'
    else:
        res = f'Success: league_id={league_id}'
    print(res)
    return res


def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'
    return 'Hello {}!'.format(escape(name))
