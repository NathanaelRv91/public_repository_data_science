import pandas as pd
import numpy as np
import matplotlib as plt
import datetime as dt
from sklearn.model_selection import cross_val_score
import sklearn.metrics
import nba_eda_functions as nba
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
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

X = nba_data[['POSITION','PLAYER_TEAM_NAME','YEAR_SEASON','ASSISTS','BLOCKS','DRB','TRB','ORB','FGA','FGM']]
y = nba_data['POINTS']

ordinal_cols = ['YEAR_SEASON']
nominal_cols = ['PLAYER_TEAM_NAME','POSITION']
numeric_cols = ['ASSISTS','BLOCKS','DRB','TRB','ORB','FGA','FGM']

pos_order = ['G','F','C']

preprocessor = ColumnTransformer(
    transformers=[
        ('ord', OrdinalEncoder(categories=pos_order), ordinal_cols),
        ('nom', OneHotEncoder(drop='first', sparse_output=False), nominal_cols),
        ('num', StandardScaler(), numeric_cols)
    ]
)

mlp_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42))
])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

mlp_pipeline.fit(X_train, y_train)

# Evaluate final test accuracy
accuracy = mlp_pipeline.score(X_test, y_test)
print(f"Test Accuracy: {accuracy:.4f}")
