import datetime
from datetime import date
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def skip_fixture(data):
    status = data['fixture']['status']['short']
    if status == 'NS' or status == 'PST' or status == 'TBD':
        return True
    return False


def get_winner_from_fixture(fixtureID):
    fixtures_ref = db.collection(u'fixtures')

    ref = fixtures_ref \
        .where('fixture.id', '==', fixtureID)

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


# Use a service account
cred = credentials.Certificate('../better-gsts-60715c303402.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# Query data
tips_ref = db.collection('eventTips')
ref = tips_ref \
    .where('created', '>=', datetime.datetime(2021, 5, 14))

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
