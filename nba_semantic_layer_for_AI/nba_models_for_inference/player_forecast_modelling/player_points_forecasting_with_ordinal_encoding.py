from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import nba_eda_functions as nb
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score


#player_data = nb.pull_player_list()
player = pd.read_csv('load_player_details.csv')
print(player.columns)
player['PLAYER_NAMES'] = player['FIRST_NAME'] + ' ' + player['LAST_NAME']

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
player_report['PLAYER_NAME'] = encoder.fit_transform(player_report[['PLAYER_NAME']])

X = player_report[['PLAYER_NAME', 'YEAR_SEASON', 'steals', 'blocks','assists', 'rebounds', 'wins']]
y = player_report['points']

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = .2,random_state =42,shuffle = True)


model = LinearRegression()

model.fit(X_train,y_train)

y_pred = model.predict(X_test)

print(f" Model R2 : {r2_score(y_test,y_pred)}")
