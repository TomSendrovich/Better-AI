import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X = pd.read_csv("model/combined.csv")
Y = X['W']
X = X.drop(columns=['HT', 'AT', 'W'])
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

randomForest = RandomForestClassifier(n_estimators=400, max_depth=6, max_features=7)
randomForest.fit(X_train, y_train)
print(randomForest.predict_proba(X_train)[0:10])

'''option to save model vectors. we can load this file later and predict with it'''
# filename = 'model/model.sav'
# pickle.dump(randomForest, open(filename, 'wb'))
# loaded_model = pickle.load(open(filename, 'rb'))
# print(loaded_model.predict_proba(X_train)[0:10])
