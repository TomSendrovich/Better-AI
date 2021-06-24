from pyrebase import pyrebase

config = {
    "apiKey": "AIzaSyBLvqjFE7V4CQSFJg_s4Rd9RJD47bBTrkY",
    "authDomain": "better-gsts.firebaseapp.com",
    "databaseURL": "fake",
    "projectId": "better-gsts",
    "storageBucket": "better-gsts.appspot.com",
    "serviceAccount": "../better-gsts-60715c303402.json"
}

firbase_storage = pyrebase.initialize_app(config)
storage = firbase_storage.storage()

# storage.child("17.PNG").put("17.PNG")
filename = "Premier League 2020-2021 - 2.csv"
storage.child(filename).download(path=filename, filename=filename)

f = open(filename)

print(f.readlines())
