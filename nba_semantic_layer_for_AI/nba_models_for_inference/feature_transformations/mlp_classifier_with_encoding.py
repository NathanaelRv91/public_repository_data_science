import pandas as pd
import numpy as np
import matplotlib as plt
import sklearn.metrics
import nba_eda_functions as nba
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report

nba_data = nba.pull_player_view()
player_list = nba.pull_player_list()
nba_data = pd.DataFrame(nba_data)
player_list = pd.DataFrame(player_list)
player_list['PLAYER_NAME'] = player_list['FIRSTNAME'] + ' ' + player_list['LASTNAME']

nba_data = pd.merge(nba_data,player_list, how = 'inner', left_on = 'PLAYER_ID', right_on = 'PERSONID')
print(nba_data.columns)
nba_data.dropna(subset=['PLAYER_NAME_x'], inplace=True)


for i in range(len(nba_data)):
    if nba_data.loc[i,'GUARD'] == 1 & nba_data.loc[i, 'FORWARD'] == 1:
        nba_data.loc[i, 'POSITION'] = "G"
    elif nba_data.loc[i,'FORWARD'] == 1 & nba_data.loc[i, 'CENTER'] == 1:
        nba_data.loc[i, 'POSITION'] = "F"
    elif nba_data.loc[i,"GUARD"] == 1:
        nba_data.loc[i, "POSITION"] = "G"
    elif nba_data.loc[i,"FORWARD"] == 1:
        nba_data.loc[i, "POSITION"] = "F"
    elif nba_data.loc[i,"CENTER"] == 1:
        nba_data.loc[i, "POSITION"] = "C"
    else:
        nba_data.loc[i, "POSITION"] = "F"

X = nba_data[['YEAR_SEASON','ASSISTS','BLOCKS','DRB','TRB','ORB','FGA','FGM']]
y = nba_data['POINTS']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

mlp = MLPClassifier(
    hidden_layer_sizes=(100, 50), # 2 hidden layers: 100 nodes, then 50 nodes
    activation='relu',            # Rectified Linear Unit activation function
    solver='adam',                # Optimization algorithm
    max_iter=300,                 # Maximum number of epochs
    random_state=42               # Ensures reproducible results
)

mlp.fit(X_train_scaled, y_train)
y_pred = mlp.predict(X_test_scaled)

print(f"Accuracy for NBA Data: {accuracy_score(y_test, y_pred):.2f}\n")
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names= X_train[['YEAR_SEASON','ASSISTS','BLOCKS','DRB','TRB','ORB','FGA','FGM']]))
