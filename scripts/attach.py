import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

LEAGUE = "Primera Division"


def skip_fixture(data):
    status = data['fixture']['status']['short']
    if status == 'NS' or status == 'PST' or status == 'TBD':
        return True
    return False


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


# Use a service account
cred = credentials.Certificate('../better-gsts-60715c303402.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# Query data
fixtures_ref = db.collection(u'fixtures')
docs = fixtures_ref.stream()

# Create a query against the collection
ref = fixtures_ref \
    .where('league.name', '==', LEAGUE)

query = ref.stream()

f2 = open(os.pardir + os.path.sep +
          LEAGUE + '.csv', 'w')

f2.write("HT,HR,HW,HL,HD,HGF,HGA,HS,AT,AR,AW,AL,AD,AGF,AGA,AS,W\n")

for doc in query:
    print(doc.id)
    data = doc.to_dict()

    if skip_fixture(data):
        continue

    home = data['teams']['home']['name']
    away = data['teams']['away']['name']
    score = '%d:%d' % (data['score']['fulltime']['home'], data['score']['fulltime']['away'])
    league = 'PL' if data['league']['id'] == 39 else 'PD'
    season = data['league']['season']
    season_round = data['league']['round'][-1]

    winner = 0 if data['teams']['home']['winner'] is None \
        else 1 if data['teams']['home']['winner'] is True \
        else 2

    # print(home, away, score, league, season, season_round, winner)

    full_league = 'Premier League' if league == 'PL' else 'Primera División'

    file_name = '%s %d-%d - %d' % (full_league, season, season + 1, int(season_round) - 1)

    if season_round != '1' and season_round != '0':
        f = open(os.pardir + os.path.sep +
                 "standings_csv" + os.path.sep +
                 league + os.path.sep +
                 str(season) + os.path.sep +
                 file_name + ".csv", "r")

        HR = HW = HL = HD = HGF = HGA = AR = AW = AL = AD = AGF = AGA = None

        for line in f.readlines():

            if line.__contains__(DB_name_to_CSV_name(home)):
                line_values = line.split(',')
                HR = line_values[0]
                HW = line_values[3]
                HD = line_values[4]
                HL = line_values[5]
                HGF = line_values[6].split(':')[0]
                HGA = line_values[6].split(':')[1]

            if line.__contains__(DB_name_to_CSV_name(away)):
                line_values = line.split(',')
                AR = line_values[0]
                AW = line_values[3]
                AD = line_values[4]
                AL = line_values[5]
                AGF = line_values[6].split(':')[0]
                AGA = line_values[6].split(':')[1]
    else:
        HR = HW = HL = HD = HGF = HGA = AR = AW = AL = AD = AGF = AGA = '0'

    f2.write(home)
    f2.write(',' + HR)
    f2.write(',' + HW)
    f2.write(',' + HL)
    f2.write(',' + HD)
    f2.write(',' + HGF)
    f2.write(',' + HGA)
    f2.write(',' + str(data['score']['fulltime']['home']))
    f2.write(',' + away)
    f2.write(',' + AR)
    f2.write(',' + AW)
    f2.write(',' + AL)
    f2.write(',' + AD)
    f2.write(',' + AGF)
    f2.write(',' + AGA)
    f2.write(',' + str(data['score']['fulltime']['away']))
    f2.write(',' + str(winner) + '\n')
