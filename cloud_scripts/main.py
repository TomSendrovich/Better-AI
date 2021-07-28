import datetime
import json
import pickle
from datetime import date

import google.cloud.firestore
import google.cloud.storage
import requests
from flask import escape
import numpy as np


def fetch_data_from_api(url):
    payload = {}
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '5453c6e17010446f88dab41a62c97a53'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    obj = json.loads(response.text)

    return obj


# to deploy function from console: 'gcloud functions deploy update_fixtures'
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
        url = f'https://v3.football.api-sports.io/fixtures?season=2020&league={league_id}'

    # connect db
    db = google.cloud.firestore.Client()
    batch = db.batch()

    # get json response
    obj = fetch_data_from_api(url=url)
    response = obj['response']
    results_count = obj['results']

    count = 0

    for json_obj in response:
        count = count + 1

        fixture_id = json_obj["fixture"]["id"]
        fixture_date = (json_obj["fixture"]["date"]).split(':')[0]

        print(f'{fixture_date}-{fixture_id}, {count / results_count * 100:.2f}%')

        doc_ref = db.collection(u'fixtures').document(f'{fixture_id}')

        fixture = json_obj["fixture"]
        league = json_obj["league"]
        teams = json_obj["teams"]
        goals = json_obj["goals"]
        score = json_obj["score"]

        # each batch.set is 1 operation
        batch.set(doc_ref, {
            'fixture': fixture,
            'league': league,
            'teams': teams,
            'goals': goals,
            'score': score,
        })

        # commit every X documents for better performance (max is 500 operations per batch)
        if count % 400 == 0:
            batch.commit()

    batch.commit()  # commit the rest of oeprations

    # print a summary line
    if date_filter:
        res = f'Success for {count} fixtures: league_id={league_id}, from={param_from}, to={param_to}'
    else:
        res = f'Success for {count} fixtures: league_id={league_id}'
    print(res)
    return res


# to deploy function from console: 'gcloud functions deploy cron'
def cron(request):
    request_args = request.args

    # check arg 'league_id'. mandatory
    if request_args and 'league_id' in request_args:
        league_id = request_args['league_id']
    else:
        msg = 'Error: league_id parameter is missing'
        print(msg)
        return msg

    today = date.today()
    minus_one_day = datetime.timedelta(days=-1)
    yesterday = today + minus_one_day

    url = f'https://us-central1-better-gsts.cloudfunctions.net/update_fixtures' \
          f'?league_id={league_id}&from={yesterday.isoformat()}&to={today.isoformat()}'

    url2 = f'https://us-central1-better-gsts.cloudfunctions.net/tag_tips' \
           f'?date={yesterday.isoformat()}'

    payload = {}
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': '5453c6e17010446f88dab41a62c97a53'
    }

    response = requests.request("GET", url2, headers=headers, data=payload)
    print(response.text)

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


def skip_fixture(data):
    status = data['fixture']['status']['short']
    if status == 'NS' or status == 'PST' or status == 'TBD':
        return True
    return False


def get_winner_from_fixture(fixtureID):
    db = google.cloud.firestore.Client()
    fixtures_ref = db.collection(u'fixtures')

    ref = fixtures_ref.where('fixture.id', '==', fixtureID)

    query = ref.stream()

    for doc in query:
        data = doc.to_dict()

        if skip_fixture(data):
            return None

        home = data['teams']['home']['winner']
        away = data['teams']['away']['winner']

        if home:
            return 1
        if away:
            return 2
        return 0


# to deploy function from console: 'gcloud functions deploy tag_tips'
def tag_tips(request):
    request_args = request.args

    # check arg 'league_id'. mandatory
    if request_args and 'date' in request_args:
        date = request_args['date']
        year = date.split('-')[0]
        month = date.split('-')[1]
        day = date.split('-')[2]
    else:
        date = datetime.datetime.now()
        iso = date.__str__().split(' ')[0]
        year = iso.split('-')[0]
        month = iso.split('-')[1]
        day = iso.split('-')[2]

    db = google.cloud.firestore.Client()

    # Query data
    tips_ref = db.collection('eventTips')
    ref = tips_ref.where('created', '>=', datetime.datetime(int(year), int(month), int(day)))

    docs = ref.stream()

    cache = {}
    count = 0

    for doc in docs:
        count = count + 1
        data = doc.to_dict()

        fixtureID = data['fixture']
        print("ID:", fixtureID)

        if fixtureID in cache:
            winner = cache[fixtureID]
        else:
            winner = get_winner_from_fixture(fixtureID)
            cache[fixtureID] = winner

        print("query count:", count, "cache size:", len(cache))

        if winner is not None:
            hit = winner == data['tipValue']

            doc_ref = db.collection(u'eventTips').document(doc.id)

            doc_ref.set({
                'isHit': hit
            }, merge=True)

    retval = 'date:{0}-{1}-{2}, query count:{3}, cache size:{4}'.format(year, month, day, count, len(cache))
    return retval


def DB_name_to_CSV_name(name):
    """
    string in expression is from DB
    string in return is from csv files
    """

    if name == 'Wolves':
        return 'Wolverhampton Wanderers'
    if name == 'Atletico Madrid':
        return 'Atlético Madrid'
    if name == 'Athletic Club':
        return 'Athletic Bilbao'
    if name == 'Deportivo La Coruna':
        return 'Deportivo La Coruña'
    if name == 'Malaga':
        return 'Málaga CF'
    if name == 'Alaves':
        return 'CD Alavés'
    if name == 'Leganes':
        return 'CD Leganés'
    if name == 'Sporting Gijon':
        return 'Sporting Gijón'
    if name == 'Sheffield Utd':
        return 'Sheffield United'
    if name == 'QPR':
        return 'Queens Park Rangers'
    if name == 'Almeria':
        return 'UD Almería'
    if name == 'Cordoba':
        return 'Córdoba CF'
    if name == 'Cadiz':
        return 'Cádiz CF'
    return name


# to deploy function from console: 'gcloud functions deploy storage'
def storage(request):
    request_args = request.args

    if request_args and 'id' in request_args:
        fixtureID = request_args['id']

        db = google.cloud.firestore.Client()

        doc_ref = db.collection(u'fixtures').document(fixtureID)
        doc = doc_ref.get()
        data = doc.to_dict()
        if data is None:
            return "fixture id not found"
        else:
            print('fixture %s found' % doc.id)

            home = data['teams']['home']['name']
            away = data['teams']['away']['name']
            league = 'PL' if data['league']['id'] == 39 else 'PD'
            season = data['league']['season']
            season_round = int(data['league']['round'].split("-")[1])
            print("season_round:", season_round)

            full_league = 'Premier League' if league == 'PL' else 'Primera División'
            file_name = '%s %d-%d - %d.csv' % (full_league, season, season + 1, int(season_round) - 1)
            print("file_name:", file_name)
            if season_round != 1 and season_round != 0:
                client = google.cloud.storage.Client()
                bucket = client.get_bucket('better-gsts.appspot.com')
                blob = bucket.get_blob(file_name)
                file_text = blob.download_as_text()
                # print(file_text)
                lines = file_text.split("\r\n")
                # print("lines:", lines)
                for line in lines:
                    if line.__contains__(DB_name_to_CSV_name(home)):
                        # print("line: ", line)
                        line_values = line.split(',')
                        HR = line_values[0]
                        HW = line_values[3]
                        HD = line_values[4]
                        HL = line_values[5]
                        HGF = line_values[6].split(':')[0]
                        HGA = line_values[6].split(':')[1]
                        HS = line_values[8]
                    if line.__contains__(DB_name_to_CSV_name(away)):
                        # print("line: ", line)
                        line_values = line.split(',')
                        AR = line_values[0]
                        AW = line_values[3]
                        AD = line_values[4]
                        AL = line_values[5]
                        AGF = line_values[6].split(':')[0]
                        AGA = line_values[6].split(':')[1]
                        AS = line_values[8]

            else:
                HR = HW = HL = HD = HGF = HGA = HS = AR = AW = AL = AD = AGF = AGA = AS = '0'

            vector = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (
                HR, HW, HL, HD, HGF, HGA, HS, AR, AW, AL, AD, AGF, AGA, AS)

            vector_np = np.array([np.fromstring(vector, dtype=int, sep=',')])
            print("vector_np:", vector_np)

            loaded_model = pickle.load(bucket.get_blob("model.sav").open(mode='rb'))
            result = loaded_model.predict_proba(vector_np)[0]
            print("model result:", result)

            doc_ref.set({
                'vector': vector,
                'prediction': result.tolist()
            }, merge=True)

            return str(result)
    else:
        return "Error: bad args"


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
