import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


players = pd.read_csv('NBA_DB_PLAYER_DETAILS.csv')
players = pd.DataFrame(players)
nba_data = pd.read_csv('nba_player_fcast_view.csv')
nba_data = pd.DataFrame(nba_data)
nba_data['PLAYER'] = nba_data['FIRST_NAME'] + ' ' + nba_data['LAST_NAME']

nba_data = nba_data.groupby(['PLAYER','PLAYER_ID','PLAYER_TEAM_NAME','YEAR_SEASON']).agg(
    points=('POINTS', 'sum'),
    rebounds=('TRB', 'sum'),
    steals=('STEALS', 'sum'),
    blocks=('BLOCKS', 'sum'),
    assists = ('ASSISTS','sum'),
    season_wins = ('WIN', 'sum')
).reset_index()

nba_data = nba_data[nba_data['YEAR_SEASON'].isin([2022,2023,2024,2025])]
nba_data.to_csv('check_player_stats_agg.csv')
# 1. Create a dummy time series dataset
date_range = range(2022,2033,1)
date_range = pd.DataFrame(date_range)
date_range.reset_index(inplace = True)
date_range.columns = ['index','YEAR']
print(date_range.columns)
np.random.seed(42)
sales = [100 + i * 3 + np.random.randint(-5, 5) for i in range(24)]

df = pd.merge(date_range,nba_data, how = 'left', left_on = 'YEAR', right_on = 'YEAR_SEASON' )
df = pd.merge(df,players, how = 'inner', left_on = 'PLAYER_ID', right_on = 'PERSONID')

df.to_csv('NBA_DB_PLAYER_PROFILE_FCAST.csv')
# 2. Feature Engineering
df["Trend"] = np.arange(len(df))
df["Lag_pts"] = df["points"].shift(1)

# Drop the first row since it won't have a lag value
df.dropna(inplace=True)
print(df.head())

# Use the first 18 months for training, last 5 months for testing
X = df[["Trend","Lag_pts",'rebounds','assists','steals','blocks','season_wins']]
y = df["points"]
pd.DataFrame(X).head(14).to_csv('check_train_data.csv')

# 4. Train-Test Split (Chronological split to prevent data leakage)
train_size = int(len(df) * 0.9)
X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
pd.DataFrame(X_train).head(14).to_csv('check_train_data.csv')


# Initialize and fit the model
model = LinearRegression()
model.fit(X_train, y_train)

print(f"Model Intercept: {model.intercept_:.2f}")
print(f"Coefficients (Trend, Lag_1): {model.coef_}")
