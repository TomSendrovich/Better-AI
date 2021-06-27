import pickle

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


X = pd.read_csv("combined.csv")
Y = X['W']
X = X.drop(columns=['HT', 'AT', 'W'])

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

randomForest = RandomForestClassifier(n_estimators=400, max_depth=6, max_features=7)
randomForest.fit(X_train,y_train)
# y_hat_test_forest = randomForest.predict(X_test)
# score_forest = accuracy_score(y_test, y_hat_test_forest)
# conf_forest = confusion_matrix(y_test, y_hat_test_forest)
# print("RandomForestClassifier")
# print(score_forest)
# print(conf_forest)
#
#
# '''predict new cases'''
# X = pd.read_csv("test.csv")
# Y = X['W']
# X = X.drop(columns=['HT', 'AT', 'W'])
# y_hat_test = randomForest.predict(X)
# score_test = accuracy_score(Y, y_hat_test)
# conf_forest = confusion_matrix(Y, y_hat_test)
# print("Test Random Forest")
# print(score_forest)
# print(conf_forest)

# print(y_hat_test)
#
# # print probabilites for each class
# print(lr.predict_proba(X))

'''option to save model vectors. we can load this file later and predict with it'''
filename = 'finalized_model.sav'
pickle.dump(randomForest, open(filename, 'wb'))

loaded_model = pickle.load(open(filename, 'rb'))

result = loaded_model.predict_proba(X)
print(result)
