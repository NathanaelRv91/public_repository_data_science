import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import io
import snowflake.connector

# Establish the connection
conn = snowflake.connector.connect(
    user='********6858841',
    password='***********027!',
    account='MNZAVFE-MM97348',
    warehouse='COMPUTE_WH',
    database='NBA_DB',
    schema='REPORTS',
    role = 'ACCOUNTADMIN'
)

cursor = conn.cursor()

SQL = """ SELECT * FROM NBA_DB.REPORTS.ALL_TIME_PLAYERS_STATISTICS WHERE YEAR_INT >= 1976"""
try:
    cursor.execute(SQL)
    one_row = cursor.fetchall()
    print("Successfully loaded data!:", one_row[100])
finally:
    cursor.close()
    conn.close()


df = pd.DataFrame(one_row)
df.columns = ['']
df.to_csv('all_time_statistics_postmerger.csv')
