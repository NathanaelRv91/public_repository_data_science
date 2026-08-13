"""Snowflake Connector to access main data used by every semantic table in this project.
Auth uses Snowflake user/pw Credentials.
"""

import pandas as pd
import numpy as np
import datetime
import snowflake.connector

def pull_player_list():
    conn = snowflake.connector.connect(
    user= 'JANDERSON6858841',
    password='********2027!',
    account='MNZAVFE-MM97348',
    warehouse='COMPUTE_WH',
    database='NBA_DB',
    schema='REPORTS',
    role = 'ACCOUNTADMIN')

    cursor = conn.cursor()
    sql_player = """
        SELECT * FROM NBA_DB.PLAYER_DATA.PLAYER_DETAILS
            """
    try:
        cursor.execute(sql_player)
        one_row_player = cursor.fetch_pandas_all()
        print("Successfully loaded data!:", one_row_player.head(5))
    finally:
        cursor.close()
        conn.close()

    df_player = pd.DataFrame(one_row_player)
    df_player.to_csv("load_player_details.csv")
    ## PLAYER DETAILS LIST ##
    #df_player.columns = ['PERSONID','FIRSTNAME','LASTNAME','BIRTHDATE','SCHOOL','COUNTRY','HEIGHTINCHES','BODYWEIGHTLBS','JERSEY','GUARD','FORWARD','CENTER','DLEAGUEFLAG','NBAFLAG','GAMESPLAYEDFLAG','DRAFTYEAR','DRAFTROUND','DRAFTNUMBER','FROMYEAR','TOYEAR']
    return df_player



def pull_player_stats():
    conn = snowflake.connector.connect(
    user='*********6858841',
    password='**********027!',
    account='MNZAVFE-MM97348',
    warehouse='COMPUTE_WH',
    database='NBA_DB',
    schema='REPORTS',
    role = 'ACCOUNTADMIN')

    cursor = conn.cursor()
    sql_stats = """
        SELECT * FROM NBA_DB.REPORTS.FCT_PLAYER_MASTER_STATS
                WHERE YEAR_SEASON >= 1976
            """
    try:
        cursor.execute(sql_stats)
        one_row_stats = cursor.fetch_pandas_all()
        print(f"Successfully loaded data!:",one_row_stats.head(5))
    finally:
        cursor.close()
        conn.close()

    df_stats = pd.DataFrame(one_row_stats)
    df_stats.to_csv('load_player_statistics_postmerger.csv')
    ## PLAYER STATS COLUMNS ##
    #df_stats.columns = ['INDEX','FIRST_NAME','LAST_NAME','PLAYER_ID','GAME_ID','GAME_DATE','PLAYER_TEAM_CITY','PLAYER_TEAM_NAME','OPP_TEAM_CITY','OPP_TEAM_NAME','SEASON_TYPE','GM_LABEL','GM_SUBLABEL','GM_NUMBER','WIN','HOME','MIN_PLAYED','POINTS','ASSISTS','BLOCKS','STEALS','FGA','FGM','FG_PCT','PT3_ATT','PT3_FGM','PT3_PCT','FTA','FTM','FT_PCT','DRB','ORB','TRB','PF','TOS','PLUS_MINUS','PLAYER_TEAM_ID','OPP_TEAM_ID','COMMENT','POS','GAME_TIMESTAMP','YEAR_INT']
    return df_stats


def pull_player_view():
    conn = snowflake.connector.connect(
    user='JANDERSON6858841',
    password='********2027!',
    account='MNZAVFE-MM97348',
    warehouse='COMPUTE_WH',
    database='NBA_DB',
    schema='REPORTS',
    role = 'ACCOUNTADMIN')

    cursor = conn.cursor()
    sql_stats = """
        SELECT * FROM NBA_DB.REPORTS.PLAYER_STATS_VIEW
                WHERE YEAR_SEASON >= 2021
            """
    try:
        cursor.execute(sql_stats)
        one_row_stats = cursor.fetch_pandas_all()
        print(f"Successfully loaded data!:",one_row_stats.head(5))
    finally:
        cursor.close()
        conn.close()

    df_player_view = pd.DataFrame(one_row_stats)
    df_player_view.to_csv('load_player_statistics_fcast_view.csv')
    ## PLAYER STATS COLUMNS ##
    #df_stats.columns = ['INDEX','FIRST_NAME','LAST_NAME','PLAYER_ID','GAME_ID','GAME_DATE','PLAYER_TEAM_CITY','PLAYER_TEAM_NAME','OPP_TEAM_CITY','OPP_TEAM_NAME','SEASON_TYPE','GM_LABEL','GM_SUBLABEL','GM_NUMBER','WIN','HOME','MIN_PLAYED','POINTS','ASSISTS','BLOCKS','STEALS','FGA','FGM','FG_PCT','PT3_ATT','PT3_FGM','PT3_PCT','FTA','FTM','FT_PCT','DRB','ORB','TRB','PF','TOS','PLUS_MINUS','PLAYER_TEAM_ID','OPP_TEAM_ID','COMMENT','POS','GAME_TIMESTAMP','YEAR_INT']
    return df_player_view

def pull_team_view():
    conn = snowflake.connector.connect(
    user='JANDERSON6858841',
    password='********2027!',
    account='MNZAVFE-MM97348',
    warehouse='COMPUTE_WH',
    database='NBA_DB',
    schema='REPORTS',
    role = 'ACCOUNTADMIN')

    cursor = conn.cursor()

    sql_teams = """CREATE OR REPLACE TABLE team_stats_temp AS (
 SELECT TEAMID,
    TEAMNAME,
    CASE WHEN EXTRACT (MONTH FROM GAMEDATE) <= 7 THEN DATE_PART(YEAR, GAMEDATE) - 1 ELSE DATE_PART(YEAR,GAMEDATE) END AS YEAR_TM,
    COUNT(DISTINCT GAMEID) AS team_games_played,
    SUM(REBOUNDSDEFENSIVE) AS team_drb,
    SUM(REBOUNDSOFFENSIVE) AS team_orb,
    SUM(REBOUNDSTOTAL) AS team_trb,
    SUM(STEALS)AS team_steals,
    SUM(ASSISTS) AS team_assists,
    SUM(BLOCKS) AS team_blocks,
    SUM(TURNOVERS) AS team_turnovers,
    SUM(Q1POINTS + Q2POINTS + Q3POINTS + Q4POINTS) AS team_points,
    SUM(THREEPOINTERSATTEMPTED) AS team_3pt_fga,
    SUM(THREEPOINTERSMADE) AS team_3pt_fgm,
    DIV0(SUM(THREEPOINTERSMADE),SUM(THREEPOINTERSATTEMPTED)) AS team_pct_3pt,
    SUM(FREETHROWSATTEMPTED) AS team_fta,
    SUM(FREETHROWSMADE) AS team_ftm,
    DIV0(SUM(FREETHROWSMADE),SUM(FREETHROWSATTEMPTED)) AS team_pct_ft,
    SUM(WIN) AS team_season_wins,
    SUM(FIELDGOALSATTEMPTED) AS team_fga,
    SUM(FIELDGOALSMADE) AS team_fgm,
    DIV0(SUM(FIELDGOALSMADE),SUM(FIELDGOALSATTEMPTED)) AS team_pct_fg
    FROM ALL_TIME_TEAM_STATISTICS
GROUP BY 1,2,3);


CREATE OR REPLACE VIEW team_stats_view AS (
    SELECT
       a.*,
       b.abbreviation,
       b.city,
       b.state,
       b.year_founded,
       c.arena,
       c.arenacapacity,
       c.owner,
       c.headcoach,
       c.generalmanager,
       c.instagram           AS instagram_link,
       c.facebook            AS fb_link,
       c.twitter             AS x_link
FROM team_stats_temp a
            JOIN TEAM_DATA.TEAM_LIST b
              ON a.teamid = b.team_id
            LEFT JOIN TEAM_DATA.TEAM_DETAILS c
               ON b.team_id = c.team_id
                );"""
    try:
        cursor.execute(sql_teams)
        one_row_stats = cursor.fetch_pandas_all()
        print(f"Successfully loaded data!:",one_row_stats.head(5))
    finally:
        cursor.close()
        conn.close()

    df_team_view = pd.DataFrame(one_row_stats)
    df_team_view.to_csv('load_team_statistics_fcast_view.csv')
    return df_team_view
