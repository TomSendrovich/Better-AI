import pickle

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier


X = pd.read_csv("combined.csv")
Y = X['W']

X = X.drop(columns=['HT', 'AT', 'W'])


X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=1)
lr = MLPClassifier(max_iter=7)
# lr = LogisticRegression(solver='liblinear',max_iter=10)
lr.fit(X_train, y_train)

# plt.plot(lr.loss_curve_)
# plt.show()

y_hat_test = lr.predict(X_test)
accuracy = pd.DataFrame({'Actual:': y_test, 'Predicted:': y_hat_test})
score = accuracy_score(y_test, y_hat_test)
conf = confusion_matrix(y_test, y_hat_test)
print("MLPClassifier")
print(score)
print(conf)

'''predict new cases'''
X = pd.read_csv("test.csv")
Y = X['W']
X = X.drop(columns=['HT', 'AT', 'W'])
y_hat_test = lr.predict(X)
score_test = accuracy_score(Y, y_hat_test)
conf_test = confusion_matrix(Y, y_hat_test)
print("Test MLPClassifier")
print(score_test)
print(conf_test)


randomForest = RandomForestClassifier(n_estimators=1000, max_depth=4, min_samples_leaf=5)
randomForest.fit(X_train,y_train)
y_hat_test_forest = randomForest.predict(X_test)
score_forest = accuracy_score(y_test, y_hat_test_forest)
conf_forest = confusion_matrix(y_test, y_hat_test_forest)
print("RandomForestClassifier")
print(score_forest)
print(conf_forest)


'''predict new cases'''
X = pd.read_csv("test.csv")
Y = X['W']
X = X.drop(columns=['HT', 'AT', 'W'])
y_hat_test = randomForest.predict(X)
score_test = accuracy_score(Y, y_hat_test)
conf_forest = confusion_matrix(Y, y_hat_test)
print("Test Random Forest")
print(score_forest)
print(conf_forest)

# print(y_hat_test)
#
# # print probabilites for each class
# print(lr.predict_proba(X))

'''option to save model vectors. we can load this file later and predict with it'''
# filename = 'finalized_model.sav'
# pickle.dump(lr, open(filename, 'wb'))
#
# loaded_model = pickle.load(open(filename, 'rb'))

# result = loaded_model.predict_proba(X)
# print(result)
