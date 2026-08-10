from sklearn.model_selection import train_test_split
from sklearn import datasets, linear_model, metrics
import pandas as pd
import numpy as np
import nba_eda_functions as nba
import snowflake.connector 

def pull_player_data_all_nba():
    conn = snowflake.connector.connect(
    user= '********858841',
    password='*******2027!',
    account='MNZAVFE-MM97348',
    warehouse='COMPUTE_WH',
    database='NBA_DB',
    schema='REPORTS',
    role = 'ACCOUNTADMIN')

    cursor = conn.cursor()
    sql_player = """
        SELECT * FROM NBA_DB.REPORTS.PLAYER_STATISTICS_10_YR_REPORT
            """
    try:
        cursor.execute(sql_player)
        one_row_player = cursor.fetch_pandas_all()
        print("Successfully loaded data!:", one_row_player.head(5))
    finally:
        cursor.close()
        conn.close()

    nba_data = pd.DataFrame(one_row_player)
    return nba_data

nba_data = pull_player_data_all_nba()
nba_data['NUMBER_TM'] = nba_data['NUMBER_TM'].fillna("NONE")
X = nba_data[['POINTS','ASSISTS','BLOCKS','STEALS','FGM','TRB','DRB','ORB']]
y = nba_data['NUMBER_TM']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=1)
pd.DataFrame(X_train).to_csv('test_x_data.csv')
reg = linear_model.LogisticRegression(max_iter=10000, random_state=0)
reg.fit(X_train, y_train)

y_pred = reg.predict(X_test)
print(f"Logistic Regression model accuracy: {metrics.accuracy_score(y_test, y_pred) * 100:.2f}%")
