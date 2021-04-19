import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.utils.validation import check_is_fitted


X = pd.read_csv("combined.csv")
Y = X['W']

X = pd.concat([X,pd.get_dummies(X['HT'],prefix='HomeTeam')],axis=1)
X = pd.concat([X,pd.get_dummies(X['AT'],prefix='AwayTeam')],axis=1)
X = X.drop(columns=['HT','AT','W'])


X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=1)
lr = MLPClassifier(max_iter=7)
#lr = LogisticRegression(solver='liblinear',max_iter=10)
lr.fit(X_train, y_train)

y_hat_test = lr.predict(X_test)
accuracy = pd.DataFrame({'Actual:':y_test,'Predicted:':y_hat_test})
score = accuracy_score(y_test,y_hat_test)
conf = confusion_matrix(y_test,y_hat_test)
print(score)
print(conf)