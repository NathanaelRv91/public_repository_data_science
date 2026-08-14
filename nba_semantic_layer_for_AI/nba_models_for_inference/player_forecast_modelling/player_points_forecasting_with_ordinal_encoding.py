import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
from collections import deque
from sklearn.preprocessing import StandardScaler
from tabulate import tabulate

#player_data = nb.pull_player_list()
player = pd.read_csv('nba_player_fcast_view.csv')
print(player.columns)
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
print(player_report.columns)
print(player_report['YEAR_SEASON'].min())

player_list = list(player_report['PLAYER_NAME'].unique())
encoder = OrdinalEncoder(categories=[player_list])
player_report['PLAYER_NAMES'] = encoder.fit_transform(player_report[['PLAYER_NAME']])

player_report.PLAYER_NAMES.to_csv('player_names.csv')

nba_players = pd.DataFrame(player_report['PLAYER_NAMES'].unique())
nba_players.columns = ['PLAYER_IDs']

X = player_report[['PLAYER_NAMES', 'YEAR_SEASON', 'steals', 'blocks','assists', 'rebounds', 'wins']]
y = player_report['points']

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = .2,random_state =42,shuffle = True)

date_range = range(2022,2034,1)
date_range = pd.DataFrame(date_range)
date_range.reset_index(inplace = True)
date_range.columns = ['index','YEAR']

date_players = pd.merge(date_range, nba_players, how = 'cross').reset_index()
date_players = date_players[['YEAR','PLAYER_IDs']]
date_players.to_csv('check_cross_nba.csv')

fcast_train = pd.merge(date_players, X_train, how = 'left', left_on = ['YEAR','PLAYER_IDs'],right_on = ['YEAR_SEASON','PLAYER_NAMES'])
fcast_train.set_index('PLAYER_IDs',inplace = True)
fcast_train.sort_index(ascending = True)
fcast_train.sort_values(by = ['YEAR'], inplace = True)
fcast_train = pd.read_csv('fcast_train_check.csv')

fcast_train['rolling_avg_rebounds'] = fcast_train['rebounds'].rolling(window=3, min_periods=1).mean()
fcast_train['rolling_avg_assists'] = fcast_train['assists'].rolling(window=3, min_periods=1).mean()
fcast_train['rolling_avg_blocks'] = fcast_train['blocks'].rolling(window=3, min_periods=1).mean()
fcast_train['rolling_avg_steals'] = fcast_train['steals'].rolling(window=3, min_periods=1).mean()
fcast_train['rolling_avg_wins'] = fcast_train['wins'].rolling(window=3, min_periods=1).mean()

fcast_train.to_csv('check_rolling_avg.csv')

for i in range(len(fcast_train)):
    if fcast_train.loc[i,'YEAR'] >= 2023:
        if pd.isna(fcast_train.loc[i,'YEAR_SEASON']):
            fcast_train.loc[i,'rolling_avg_wins'] = fcast_train.loc[i-1,'rolling_avg_wins'] * 1.025
            fcast_train.loc[i, 'rolling_avg_rebounds'] = fcast_train.loc[i - 1, 'rolling_avg_rebounds'] * 1.025
            fcast_train.loc[i, 'rolling_avg_assists'] = fcast_train.loc[i - 1, 'rolling_avg_assists'] * 1.025
            fcast_train.loc[i, 'rolling_avg_blocks'] = fcast_train.loc[i - 1, 'rolling_avg_blocks'] * 1.025
            fcast_train.loc[i, 'rolling_avg_steals'] = fcast_train.loc[i - 1, 'rolling_avg_steals'] * 1.025

fcast_train.to_csv('check_rolling_avg.csv')

model = LinearRegression()
model.fit(X_train,y_train)

X_train_fcast = fcast_train[['PLAYER_IDs','YEAR','rolling_avg_steals','rolling_avg_blocks','rolling_avg_assists','rolling_avg_rebounds','rolling_avg_wins']]
X_train_fcast.columns = ['PLAYER_NAMES', 'YEAR_SEASON', 'steals', 'blocks','assists', 'rebounds', 'wins']
X_train_fcast = pd.DataFrame(X_train_fcast)
X_train_fcast.dropna(subset = ['wins'],inplace = True)
X_train_fcast.to_csv('test_fcast_analysis.csv')

multipliers = list(model.coef_)
multipliers = [[x] for x in multipliers]
multipliers = pd.DataFrame(multipliers)
list_features = ['PLAYER_NAMES', 'YEAR_SEASON', 'steals', 'blocks','assists', 'rebounds', 'wins']
list_features = [[x] for x in list_features]
list_features = pd.DataFrame(list_features)
coeff_predictors = pd.concat([list_features, multipliers], axis = 1)
coeff_predictors.columns = ['Feature_Name','COEFF']
print(coeff_predictors)

player_transform = coeff_predictors.iloc[0,1]
season_transform = coeff_predictors.iloc[1,1]
steals_transform = coeff_predictors.iloc[2,1]
blocks_transform = coeff_predictors.iloc[3,1]
assists_transform = coeff_predictors.iloc[4,1]
rebounds_transform = coeff_predictors.iloc[5,1]
wins_transform = coeff_predictors.iloc[6,1]

X_train_fcast.reset_index(inplace = True)
### RUN Forecasting on 2026 - 2033 Seasons for all Active Players ###
for i in range(len(X_train_fcast)):
    if X_train_fcast.loc[i,'YEAR_SEASON'] >= 2025:
        X_train_fcast.loc[i, 'PLAYER_NAMES'] = X_train_fcast.loc[i, 'PLAYER_NAMES'] * player_transform
        X_train_fcast.loc[i, 'PLAYER_MULT'] = X_train_fcast.loc[i, 'YEAR_SEASON'] * season_transform
        X_train_fcast.loc[i, 'steals'] = X_train_fcast.loc[i, 'steals'] * steals_transform
        X_train_fcast.loc[i, 'blocks'] = X_train_fcast.loc[i, 'PLAYER_NAMES'] * blocks_transform
        X_train_fcast.loc[i, 'assists'] = X_train_fcast.loc[i, 'assists'] * assists_transform
        X_train_fcast.loc[i, 'rebounds'] = X_train_fcast.loc[i, 'rebounds'] * rebounds_transform
        X_train_fcast.loc[i, 'wins'] = X_train_fcast.loc[i, 'wins'] * wins_transform
        X_train_fcast['points'] = X_train_fcast.loc[i, 'PLAYER_NAMES'] * X_train_fcast.loc[i, 'PLAYER_MULT'] * X_train_fcast.loc[i, 'steals'] * \
                                        X_train_fcast.loc[i, 'assists'] * X_train_fcast.loc[i, 'rebounds'] * X_train_fcast.loc[i, 'wins']



y_pred = model.predict(X_test)
y_pred = pd.Series(y_pred)
print(f" Model for Base R2: {r2_score(y_test,y_pred)}")


pred_series = pd.Series(y_pred, index=X_test.index, name="Predicted_Value")
result_df = pd.concat([X_test,pred_series], axis = 1)
result_df.to_csv('base_model_fcast.csv')
