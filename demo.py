import datetime
from datetime import date

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# # Use the application default credentials
# cred = credentials.ApplicationDefault()
# firebase_admin.initialize_app(cred, {
#     'projectId': 'better-gsts',
# })

# Use a service account
cred = credentials.Certificate('better-gsts-60715c303402.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# # Add data
# doc_ref = db.collection(u'users').document(u'alovelace')
# doc_ref.set({
#     u'first': u'Ada',
#     u'last': u'Lovelace',
#     u'born': 1815
# })
#
# # Add another data
# doc_ref = db.collection(u'users').document(u'aturing')
# doc_ref.set({
#     u'first': u'Alan',
#     u'middle': u'Mathison',
#     u'last': u'Turing',
#     u'born': 1912
# })

# # Read data
# teams_ref = db.collection(u'teams')
# docs = teams_ref.stream()
# for doc in docs:
#     print(f'{doc.id} => {doc.to_dict()}')

# Query data
fixtures_ref = db.collection(u'fixtures')
docs = fixtures_ref.stream()

today = date.today()
one_week = datetime.timedelta(days=-7)
last_week = today + one_week
print("Today's date:", today.isoformat())
print("Last week's date:", last_week.isoformat())

# Create a query against the collection
past_games_query_ref = fixtures_ref.where(u'fixture.date', u'<', today.isoformat())

upcoming_games_query_ref = fixtures_ref \
    .where(u'fixture.date', u'>=', last_week.isoformat()) \
    .where(u'fixture.date', u'<=', today.isoformat())

query = upcoming_games_query_ref.stream()

for doc in query:
    print(f'{doc.id} => {doc.to_dict()}')
