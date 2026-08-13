""" A conservative slightly linear model that adds a subtle scoring 'lift' to any of the 30 NBA teams: 
multiple linear regression model that pulls a cortex AI sentiment function further downstream of scoring performance for each in NBA team from internal snowflake staging! 
This intermediate forcast is designed to show how we can create a function for this process and feed into a clean Streamlit App. 
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error,r2_score

# 1. Create a dummy time series dataset (e.g., Monthly Sales)
nba_data = pd.read_csv('NBA_DB_TEAM_STATS.csv')
nba_data = pd.DataFrame(nba_data)
nba_data = nba_data[nba_data.YEAR_TM >= 2020]
nba_data.sort_values(by = ['TEAMNAME','YEAR_TM'], inplace = True)
nba_data = nba_data.groupby(['TEAMNAME','YEAR_TM']).agg(
    team_points=('TEAM_POINTS', 'sum'),
    team_rebounds=('TEAM_TRB', 'sum'),
    team_steals=('TEAM_STEALS', 'sum'),
    team_blocks=('TEAM_BLOCKS', 'sum'),
    team_assists = ('TEAM_ASSISTS','sum'),
    season_wins = ('TEAM_SEASON_WINS', 'max')

).reset_index()

## Bad Data for Covid so we need to impute values by asuming scoring increased by 3.5% for all teams: basketball_reference.com
for i in range(len(nba_data)):
    if nba_data.loc[i,'YEAR_TM'] == 2021:
        nba_data.loc[i,'team_points'] = 1.035 * nba_data.loc[i-1,'team_points']
    else:
        pass
nba_data.to_csv('check_team_agg.csv')
np.random.seed(42)
print(nba_data['YEAR_TM'].min())
date_range = range(2016,2034,1)
date_range = pd.DataFrame(date_range)
date_range.reset_index(inplace = True)
date_range.columns = ['index','YEAR']
print(date_range.columns)
pd.DataFrame(date_range).to_csv('date_range_check.csv')
#nba_data['YEAR_SEASON'] = pd.to_datetime(nba_data['YEAR_SEASON'])
df = pd.merge(date_range, nba_data, how = 'left', left_on = 'YEAR', right_on = 'YEAR_TM')
#sales_trend = np.linspace(10, 50, 36)  # Linear upward trend
#noise = np.random.normal(0, 2, 36)     # Random fluctuations
nba_data.sort_values(by = ['TEAMNAME','YEAR_TM'])
nba_data.to_csv('nba_mapped_to_time_series.csv')
# 2. Feature Engineering: Time Step & Lag Features
df["Time_Step"] = np.arange(len(df))  # Captures linear trend (0, 1, 2...)
df["Lag_pts"] = df["team_points"].shift(1)    # Captures what happened last month

# Drop rows with NaN values caused by shifting
df.dropna(inplace=True)
df.reset_index(inplace = True)

df = df[df['TEAMNAME'] == 'Nuggets']
# 3. Split into Features (X) and Target (y)
X = df[["Time_Step","Lag_pts",'team_rebounds','team_assists','team_steals','team_blocks']]
y = df["team_points"]
pd.DataFrame(X).head(14).to_csv('check_train_data.csv')

# 4. Train-Test Split (Chronological split to prevent data leakage)
train_size = int(len(df) * 0.9)
X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
pd.DataFrame(X_train).head(14).to_csv('check_train_data.csv')
# 5. Initialize and Fit the Linear Regression Model
model = LinearRegression()
model.fit(X_train, y_train)
# 6. Make Predictions on the Test Set
y_pred = model.predict(X_test)

# Calculate Error Metric
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
coeff = model.coef_
print(f" R2 Score with 6 Features: {model.score(X_test,y_test)}")
print(f"Test Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"model coeff: {str(coeff)}")

# 7. Multi-step Future Forecasting (Recursive Strategy)
# To forecast past the test set, we iteratively use previous predictions as the new lag feature
future_steps = 9
future_predictions = []

# Start from the last known data point in the test set
last_time_step = X_test[["Time_Step","Lag_pts",'team_rebounds','team_assists','team_steals','team_blocks']].iloc[-1]
last_lag = y_test.iloc[-1]
print(last_lag)

for i in range(1, future_steps + 1):
    next_time_step = last_time_step + i
    # Predict the next step using the current time step and the last lag value
    next_pred = model.predict([next_time_step])
    future_predictions.append(next_pred)
    # Update the lag variable to be the prediction we just made
    last_lag = next_pred


future_predictions = pd.DataFrame(future_predictions)
pd.DataFrame(y_pred).to_csv('model_predictions.csv')
# Generate future dates for plotting
future_dates = range(2025,2034,1)
pred_range = range(2020,2025,1)

# 8. Visualize Results
plt.figure(figsize=(10, 5))
plt.plot(df['YEAR_TM'], df["team_points"], label="Actual Data", color="black")
plt.plot(2025, y_pred, label="Test Prediction for 2025", color="blue", marker="x",markersize=20)
plt.plot(future_dates, future_predictions, label="Out-of-Sample Forecast", color="red", marker="o")
plt.legend()
plt.title("Time Series Forecasting with Linear Regression")
plt.grid(True)
plt.show()


