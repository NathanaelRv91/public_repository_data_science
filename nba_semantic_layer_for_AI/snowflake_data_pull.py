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

SQL_players = """ SELECT * FROM NBA_DB.PLAYER_DATA.PLAYER_DETAILS """
try:
    cursor.execute(SQL_players)
    one_row_playrs = cursor.fetchall()
    print("Successfully loaded data!:", one_row_players[100])
finally:
    cursor.close()
    conn.close()

df_players = pd.DataFrame(one_row_players)
## PLAYER DETAILS LIST ##
df_players.columns = ['PERSONID','FIRSTNAME','LASTNAME','BIRTHDATE','SCHOOL','COUNTRY','HEIGHTINCHES','BODYWEIGHTLBS','JERSEY','GUARD','FORWARD','CENTER','DLEAGUEFLAG','NBAFLAG','GAMESPLAYEDFLAG','DRAFTYEAR','DRAFTROUND','DRAFTNUMBER','FROMYEAR','TOYEAR']


SQL_players = """ SELECT * FROM NBA_DB.PLAYER_DATA.PLAYER_DETAILS """
try:
    cursor.execute(SQL_players)
    one_row_playrs = cursor.fetchall()
    print("Successfully loaded data!:", one_row_players[100])
finally:
    cursor.close()
    conn.close()

df_players = pd.DataFrame(one_row_players)

## SEASON STATS Fct Table ## 
df_stats.columns = ['INDEX','FIRST_NAME','LAST_NAME','PLAYER_ID','GAME_ID','GAME_DATE','PLAYER_TEAM_CITY','PLAYER_TEAM_NAME','OPP_TEAM_CITY','OPP_TEAM_NAME','SEASON_TYPE','GM_LABEL','GM_SUBLABEL','GM_NUMBER','WIN','HOME','MIN_PLAYED','POINTS','ASSISTS','BLOCKS','STEALS','FGA','FGM','FG_PCT','PT3_ATT','PT3_FGM','PT3_PCT','FTA','FTM','FT_PCT','DRB','ORB','TRB','PF','TOS','PLUS_MINUS','PLAYER_TEAM_ID','OPP_TEAM_ID','COMMENT','POS','GAME_TIMESTAMP','YEAR_INT']
df_stats.to_csv('all_player_season_statistics_training.csv')
