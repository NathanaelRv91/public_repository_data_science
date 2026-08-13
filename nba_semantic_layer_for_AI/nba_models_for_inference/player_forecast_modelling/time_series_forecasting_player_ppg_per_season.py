import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler


players = pd.read_csv('NBA_DB_PLAYER_DETAILS.csv')
players = pd.DataFrame(players)
nba_data = pd.read_csv('nba_player_fcast_view.csv')
nba_data = pd.DataFrame(nba_data)
nba_data['PLAYER'] = nba_data['FIRST_NAME'] + ' ' + nba_data['LAST_NAME']

nba_data = nba_data.groupby(['PLAYER_ID','YEAR_SEASON']).agg(
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

df = pd.merge(date_range,nba_data, how = 'outer', left_on = 'YEAR', right_on = 'YEAR_SEASON' )
df = pd.merge(df,players, how = 'left', left_on = 'PLAYER_ID', right_on = 'PERSONID')

df.to_csv('NBA_DB_PLAYER_PROFILE_FCAST.csv')
# 2. Feature Engineering
df["Trend"] = np.arange(len(df))
df["Lag_pts"] = df["points"].shift(1)

# Drop the first row since it won't have a lag value
df.dropna(inplace=True)
print(df.head())

## Feature Scalling


# Use the first 18 months for training, last 5 months for testing
X = df[["YEAR_SEASON","PLAYER_ID","Lag_pts",'rebounds','assists','steals','blocks','season_wins']]
y = df["points"]
pd.DataFrame(X).to_csv('check_train_data.csv')

scaler = StandardScaler()

# Fit and transform the training data
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled)
# 4. Train-Test Split (Chronological split to prevent data leakage)
train_size = int(len(df) * 0.8)
X_train, X_test = X_scaled.iloc[:train_size], X_scaled.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
pd.DataFrame(X_train).head(14).to_csv('check_train_data.csv')
X_test.columns = ['YEAR_SEASON','PLAYER_ID','Lag_pts','rebounds','assists','steals','blocks','season_wins']

# Initialize and fit the model
model = LinearRegression()
model.fit(X_train, y_train)
model.predict(X_test)

print(f"Model Intercept: {model.intercept_:.2f}")
print(f"Coefficients (6 Features): {model.coef_}")

# Recursive forecasting loop
predictions = []
last_lag = y_train.iloc[-1]  # Start with the last known true sales value
current_trend = X_test[['YEAR_SEASON','PLAYER_ID','Lag_pts','rebounds','assists','steals','blocks','season_wins']].iloc[0]  # Start at the first test trend index

for i in range(len(X_test)):
    # Structure the inputs exactly like the training columns
    input_features = np.array([current_trend])

    # Predict the next step
    pred = model.predict(input_features)
    predictions.append(pred)

    # Update variables for the next iteration
    last_lag = pred  # The prediction becomes the next step's lag
    current_trend += 1  # Increment the trend counter

# Add predictions to test DataFrame
test = X_test.copy()
test["Predictions"] = predictions
pd.DataFrame(predictions).to_csv('test_predictions.csv')

rmse = np.sqrt(mean_squared_error(test["points"], test["Predictions"]))
print(f"Validation RMSE: {rmse:.2f}")

# Display actual vs predicted
print(test[["points", "Predictions"]])

