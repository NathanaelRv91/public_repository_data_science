import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import io
import snowflake.connector

# Establish the connection
conn = snowflake.connector.connect(
    user='janderson6858841',
    password='JamesRVandNcr2027!',
    account='MNZAVFE-MM97348',
    warehouse='COMPUTE_WH',
    database='NBA_DB',
    schema='REPORTS',
    role = 'ACCOUNTADMIN'
)

cursor = conn.cursor()
try:
    cursor.execute("SELECT CURRENT_VERSION()")
    one_row = cursor.fetchone()
    print("Successfully connected! Snowflake Version:", one_row[0])
finally:
    cursor.close()
    conn.close()
