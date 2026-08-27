from sklearn.model_selection import train_test_split
from sklearn import datasets, linear_model, metrics
import pandas as pd
import numpy as np
import array
import nba_eda_functions AS nba

## Predict if a player will retire --
nba_data = nba.pull_10_year_report()
nba_data['NUMBER_TM'] = nba_data['NUMBER_TM'].fillna("NONE")

X = nba_data[['FROMYEAR','FGM','FT_PCT','POINTS','FTM','TOS','DRB','ORB']]
y = nba_data['IS_ACTIVE']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=1)
pd.DataFrame(X_train).to_csv('test_x_data.csv')
reg = linear_model.LogisticRegression(max_iter=10000, random_state=42)
reg.fit(X_train, y_train)

y_pred = reg.predict(X_test)

print(f"Logistic Regression model accuracy: {metrics.accuracy_score(y_test, y_pred) * 100:.2f}%")
y_pred = pd.DataFrame(y_pred)
y_pred.to_csv('test_fcast_model_test.csv')
y_pred = pd.DataFrame(y_pred)
y_pred.columns = ['RETIRED']
print(y_pred.head())

## PASS A random player profile into predict to see if they are likely to retire next season --
y_pred['player_fcst'] = np.where(y_pred['RETIRED'] == 1, "RETIRED", "NOT RETIRED YET!")
print(y_pred)
  

  
