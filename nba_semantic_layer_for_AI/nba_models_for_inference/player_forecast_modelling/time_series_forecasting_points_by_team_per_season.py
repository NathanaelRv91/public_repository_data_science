-- This Model takes 5 years of player history from 2021 through 2025 and trains the 2026 season that completed in June for the supervised learning set -- 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import nba_eda_functions as nba

nba_data = nba.pull_player_stats()
nba_data = pd.DataFrame(nba_data)
nba_data = nba_data.groupby(['PLAYER_TEAM_NAME','YEAR_SEASON']).agg(
    team_points=('POINTS', 'sum'),
    team_rebounds=('TRB', 'sum'),
    team_steals=('STEALS', 'sum'),
    team_blocks=('BLOCKS', 'sum'),
    team_assists = ('ASSISTS','sum')
).reset_index()
np.random.seed(42)
date_range = range(2016,2035,1)
date_range = pd.DataFrame(date_range)
date_range.reset_index(inplace = True)
date_range.columns = ['index','YEAR']
print(date_range.columns)
pd.DataFrame(date_range).to_csv('date_range_check.csv')
#nba_data['YEAR_SEASON'] = pd.to_datetime(nba_data['YEAR_SEASON'])
nba_data.to_csv('check_data_config_setup.csv')
df = pd.merge(date_range, nba_data, how = 'left', left_on = 'YEAR', right_on = 'YEAR_SEASON')
sales_trend = np.linspace(10, 50, 36)  # Linear upward trend
noise = np.random.normal(0, 2, 36)     # Random fluctuations

# 2. Feature Engineering: Time Step & Lag Features
df["Time_Step"] = np.arange(len(df))  # Captures linear trend (0, 1, 2...)
df["Lag_pts"] = df["team_points"].shift(1)    # Captures what happened last month

# Drop rows with NaN values caused by shifting
df.dropna(inplace=True)
df.reset_index(inplace = True)

list_teams = pd.Series(nba_data['PLAYER_TEAM_NAME'].unique())
for i in list_teams:
  df = df[df['PLAYER_TEAM_NAME'] == 'Lakers']
  # 3. Split into Features (X) and Target (y)
  X = df[["Time_Step", "Lag_pts"]]
  y = df["team_points"]

# 4. Train-Test Split (Chronological split to prevent data leakage)
  train_size = int(len(df) * 0.8)
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
  print(f"Test Root Mean Squared Error (RMSE): {rmse:.2f}")

# 7. Multi-step Future Forecasting (Recursive Strategy)
# To forecast past the test set, we iteratively use previous predictions as the new lag feature
  future_steps = 56
  future_predictions = []

# Start from the last known data point in the test set
  last_time_step = X_test["Time_Step"].iloc[-1]
  last_lag = y_test.iloc[-1]

  for i in range(1, future_steps + 1):
      next_time_step = last_time_step + i
    # Predict the next step using the current time step and the last lag value
      next_pred = model.predict([[next_time_step, last_lag]])[0]
      future_predictions.append(next_pred)
    # Update the lag variable to be the prediction we just made
      last_lag = next_pred

# Generate future dates for plotting
  future_dates = pd.date_range(start=df.index[-1] + 15, periods=future_steps, freq="YS")

# 8. Visualize Results
  plt.figure(figsize=(10, 5))
  plt.plot(df.index, df["team_points"], label="Actual Data", color="black")
  plt.plot(y_test.index, y_pred, label="Test Predictions", color="blue", linestyle="--")
  plt.plot(future_dates, future_predictions, label="Out-of-Sample Forecast", color="red", marker="o")
  plt.legend()
  plt.title("Time Series Forecasting with Linear Regression")
  plt.grid(True)
  plt.show()
