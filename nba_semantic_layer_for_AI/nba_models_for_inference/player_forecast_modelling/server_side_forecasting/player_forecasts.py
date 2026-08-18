!pip install -r requirements.txt

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
from collections import deque
from sklearn.preprocessing import StandardScaler
from tabulate import tabulate
import nba_eda_functions as nba

from datetime import date
from datetime import time 
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector as sconn

from snowflake.snowpark.context import get_active_session
session = get_active_session()

player_data = nb.pull_player_list()
player_data = player_data.to_pandas()
player['PLAYER_NAME'] = player['FIRST_NAME'] + ' ' + player['LAST_NAME']
player_data = player[['PLAYER_NAME','PLAYER_TEAM_NAME','YEAR_SEASON','BLOCKS','STEALS','ASSISTS','TRB','POINTS','FT_PCT','WIN']]

player_report = player_data.groupby(['PLAYER_NAME','YEAR_SEASON']).agg(
    points = ('POINTS','sum'),
    steals = ('STEALS','sum'),
    blocks=('BLOCKS', 'sum'),
    assists=('ASSISTS', 'sum'),
    rebounds=('TRB', 'sum'),
    wins=('WIN', 'sum')
).reset_index()
player_report.reset_index(inplace = True)

player_list = list(player_report['PLAYER_NAME'].unique())
encoder = OrdinalEncoder(categories=[player_list])
player_report['PLAYER_NAMES'] = encoder.fit_transform(player_report[['PLAYER_NAME']])
player_report['PLAYER_NAMES'] = player_report['PLAYER_NAMES'].astype(int)
player_report.reset_index(inplace = True)
player_report.to_csv('evaluate_player_report.csv')

nba_players = pd.DataFrame(player_report['PLAYER_NAMES'].unique())
nba_players.columns = ['PLAYER_ID']

date_range = range(2016,2034,1)
date_range = pd.DataFrame(date_range)
date_range.reset_index(inplace = True)
date_range.columns = ['index','YEAR']

date_players = pd.merge(date_range, nba_players, how = 'cross').reset_index()
date_players['PLAYER_ID'] = date_players['PLAYER_ID'].astype(int)
date_players = date_players[['YEAR','PLAYER_ID']]

fcast_base = pd.merge(date_players,player_report, how = 'left', left_on = ['YEAR','PLAYER_ID'], right_on = ['YEAR_SEASON','PLAYER_NAMES'])

## ADD benchmark for players based on career averages (last 10 seasons) ##
player_bmark = player_report.groupby(['PLAYER_NAME']).agg(
points = ('points','mean'),
    steals = ('steals','mean'),
    blocks=('blocks', 'mean'),
    assists=('assists', 'mean'),
    rebounds=('rebounds', 'mean'),
    wins=('wins', 'mean'),
    last_season = ('YEAR_SEASON','max'),
    seasons = ('YEAR_SEASON','count')
).reset_index()

fcast_players = pd.merge(fcast_base, player_bmark, how = 'left', on = 'PLAYER_NAME')
fcast_players['last_season'].fillna(2025,inplace = True)
fcast_players = fcast_players[fcast_players.last_season == 2025]
fcast_players.drop(columns = ['level_0'], inplace = True)
fcast_players.sort_values(by = ['PLAYER_ID','YEAR'], ascending = True)
fcast_players.reset_index(inplace = True)

for i in range(len(fcast_players)):
    if fcast_players.loc[i,'YEAR'] > 2025:
        if pd.isna(fcast_players.loc[i-1,'YEAR_SEASON']):
            pass
        else:
            fcast_players.loc[i, 'seasons'] = fcast_players.loc[i - 1, 'seasons'] + 1
            fcast_players.loc[i, 'multiplier'] = np.where(fcast_players.loc[i, 'seasons'] <= 8, 1.03, .88)
            fcast_players.loc[i,'steals_y'] = fcast_players.loc[i - 1,'steals_y']
            fcast_players.loc[i, 'blocks_y'] = fcast_players.loc[i - 1, 'blocks_y']
            fcast_players.loc[i, 'assists_y'] = fcast_players.loc[i - 1, 'assists_y']
            fcast_players.loc[i, 'rebounds_y'] = fcast_players.loc[i - 1, 'rebounds_y']
            fcast_players.loc[i, 'wins_y'] = fcast_players.loc[i - 1, 'wins_y']
            fcast_players.loc[i, 'PLAYER_NAME'] = fcast_players.loc[i - 1, 'PLAYER_NAME']
            fcast_players.loc[i, 'PLAYER_NAMES'] = fcast_players.loc[i - 1, 'PLAYER_NAMES']
            fcast_players.loc[i,'YEAR_SEASON'] = fcast_players.loc[i-1,'YEAR_SEASON'] + 1

fcast_players.dropna(subset = ['PLAYER_NAME'], inplace = True)
fcast_players.reset_index(inplace = True)
for i in range(len(fcast_players)):
    if fcast_players.loc[i, 'YEAR'] > 2025:
        fcast_players.loc[i, 'steals_x'] = (.7 * fcast_players.loc[i - 1, 'steals_x'] + .3 * fcast_players.loc[i,'steals_y']) * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'blocks_x'] = (.7 * fcast_players.loc[i - 1, 'blocks_x'] + .3 * fcast_players.loc[
            i, 'blocks_y']) * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'assists_x'] = (.7 * fcast_players.loc[i - 1, 'assists_x'] + .3 * fcast_players.loc[
            i, 'assists_y']) * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'rebounds_x'] = (.7 * fcast_players.loc[i - 1, 'rebounds_x'] + .3 * fcast_players.loc[
            i, 'rebounds_y']) * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'wins_x'] = .7 * fcast_players.loc[i - 1, 'wins_x'] + .3 * fcast_players.loc[
            i, 'wins_y']

fcast_base = fcast_base[fcast_base.YEAR_SEASON <= 2025]
fcast_x_train = fcast_base[fcast_base.PLAYER_ID <= 900]
fcast_x_test = fcast_base[fcast_base.PLAYER_ID > 900]

fcast_x_set = fcast_x_train[['PLAYER_NAMES', 'YEAR_SEASON', 'steals', 'blocks','assists', 'rebounds', 'wins']]
fcast_y_set = fcast_x_train['points']

fcast_x_set2 = fcast_x_test[['PLAYER_NAMES', 'YEAR_SEASON', 'steals', 'blocks','assists', 'rebounds', 'wins']]
fcast_y_set2 = fcast_x_test['points']

X = player_report[['PLAYER_NAMES', 'YEAR_SEASON', 'steals', 'blocks','assists', 'rebounds', 'wins']]
y = player_report['points']

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = .2,random_state =42,shuffle = False)

model_scaler = MinMaxScaler()
X_train['YEAR_SEASON'] = model_scaler.fit_transform(pd.DataFrame(X_train['YEAR_SEASON']))
X_test['YEAR_SEASON'] = model_scaler.fit_transform(pd.DataFrame(X_test['YEAR_SEASON']))

fcast_x_set['YEAR_SEASON'] = model_scaler.fit_transform(pd.DataFrame(fcast_x_set['YEAR_SEASON']))
fcast_x_set2['YEAR_SEASON'] = model_scaler.fit_transform(pd.DataFrame(fcast_x_set2['YEAR_SEASON']))

model = LinearRegression()
model.fit(X_train,y_train)

y_pred = model.predict(X_test)
#y_pred = pd.DataFrame(y_pred)
#X_test = pd.DataFrame(X_test)
full_model = pd.concat([X_test, pd.Series(y_pred, name='points', index=X_test.index)], axis=1)

multipliers = list(model.coef_)
multipliers = [[x] for x in multipliers]
multipliers = pd.DataFrame(multipliers)
list_features = ['PLAYER_NAMES', 'YEAR_SEASON', 'steals', 'blocks','assists', 'rebounds', 'wins']
list_features = [[x] for x in list_features]
list_features = pd.DataFrame(list_features)
coeff_predictors = pd.concat([list_features, multipliers], axis = 1)
coeff_predictors.columns = ['Feature_Name','COEFF']

y_pred_train = model.predict(fcast_x_set)
full_model_2 = pd.concat([fcast_x_set, pd.Series(y_pred_train, name='points', index=fcast_x_set.index)], axis=1)

full_model_2.to_csv('full_model_2.csv')
r2 = r2_score(fcast_y_set, y_pred_train)
print(f"R2 for train test group 1: {r2}")

y_pred_train2 = model.predict(fcast_x_set2)
full_model_3 = pd.concat([fcast_x_set2, pd.Series(y_pred_train2, name='points', index=fcast_x_set2.index)], axis=1)

full_model_3.to_csv('full_model_3.csv')
r2_set2 = r2_score(fcast_y_set2, y_pred_train2)
print(f"R2 for train test group 2: {r2_set2}")

## EXECUTE Inference using our benchmark player metrics by PLAYER_ID/SEASON & Merge back with the master player names LIST ##
player_transform = coeff_predictors.iloc[0,1]
season_transform = coeff_predictors.iloc[1,1]
steals_transform = coeff_predictors.iloc[2,1]
blocks_transform = coeff_predictors.iloc[3,1]
assists_transform = coeff_predictors.iloc[4,1]
rebounds_transform = coeff_predictors.iloc[5,1]
wins_transform = coeff_predictors.iloc[6,1]
fcast_players['YEAR_SEASON'] = model_scaler.fit_transform(pd.DataFrame(fcast_players['YEAR_SEASON']))
print(assists_transform)

for i in range(len(fcast_players)):
    if fcast_players.loc[i,'YEAR'] > 2025:
        fcast_players.loc[i, 'PLAYER_NAMES'] = fcast_players.loc[i, 'PLAYER_NAMES'] * player_transform
        fcast_players.loc[i,'YEAR_SEASON'] = fcast_players.loc[i, 'YEAR_SEASON'] * season_transform * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'steals_x'] = fcast_players.loc[i, 'steals_x'] * steals_transform * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'blocks_x'] = fcast_players.loc[i, 'blocks_x'] * blocks_transform * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'assists_x'] = fcast_players.loc[i, 'assists_x'] * assists_transform * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'rebounds_x'] = fcast_players.loc[i, 'rebounds_x'] * rebounds_transform * fcast_players.loc[i,'multiplier']
        fcast_players.loc[i, 'wins_x'] = fcast_players.loc[i, 'wins_x'] + wins_transform * fcast_players.loc[i,'multiplier']

fcast_players['points_x'] = np.where(fcast_players['YEAR'] > 2025,fcast_players['PLAYER_NAMES'] + fcast_players['YEAR_SEASON'] + fcast_players['steals_x'] + \
                                        fcast_players['assists_x'] + fcast_players['rebounds_x'] + fcast_players['wins_x'],fcast_players['points_x'])



print(f" Model Preview: "\n"
  f"fcast_players[fcast_players.PLAYER_ID == 6]")



