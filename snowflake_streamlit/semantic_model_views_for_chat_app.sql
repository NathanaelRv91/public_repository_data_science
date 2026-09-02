-- All of my chat models in the YAML source are derived by my model views BELOW which give rise to an efficient data cach that runs during the deployed Streamlit App 

USE ACCOUNTADMIN;

CREATE OR REPLACE VIEW NBA_DB.REPORTS.PLAYER_SEASON_STATS AS

SELECT
    p.PLAYER_ID,
    p.FULL_NAME,

    t.TEAM_ID,

    p.TEAM_NAME,

    p.YEAR_SEASON AS SEASON,

    p.POINTS_2025 AS POINTS,
    p.ASSISTS_2025 AS ASSISTS,
    p.TRB_2025 AS REBOUNDS,
    p.STEALS_2025 AS STEALS,
    p.BLOCKS_2025 AS BLOCKS

FROM NBA_DB.REPORTS.FCT_PLAYER_MASTER_STATS p

LEFT JOIN NBA_DB.REPORTS.FCT_TEAM_MASTER_STATS t
    ON p.TEAM_NAME = t.TEAM_NAME
;

CREATE OR REPLACE VIEW NBA_DB.REPORTS.TEAM_SEASON_STATS AS

SELECT
    TEAM_ID,
    TEAM_NAME,
    ABBREVIATION,
    CITY,
    STATE,
    YEAR_FOUNDED,
    ARENA,
    OWNER,
    HEADCOACH,
    YEAR_TM AS SEASON,
    TM_POINTS_2022 AS POINTS,
    TM_ASSISTS_2022 AS ASSISTS,
    TM_STEALS_2022 AS STEALS,
    TM_BLOCKS_2022 AS BLOCKS,
    TM_TRB_2022 AS REBOUNDS,
    TM_WINS_2022 AS WINS,
    TM_FG_PCT_2022 AS FIELD_GOAL_PERCENTAGE,
    TM_PT3_PCT_2022 AS THREE_POINT_PERCENTAGE,
    TM_FT_PCT_2022 AS FREE_THROW_PERCENTAGE
FROM NBA_DB.REPORTS.FCT_TEAM_MASTER_STATS
WHERE YEAR_TM = 2022

UNION ALL

SELECT
    TEAM_ID,
    TEAM_NAME,
    ABBREVIATION,
    CITY,
    STATE,
    YEAR_FOUNDED,
    ARENA,
    OWNER,
    HEADCOACH,
    YEAR_TM AS SEASON,
    TM_POINTS_2023,
    TM_ASSISTS_2023,
    TM_STEALS_2023,
    TM_BLOCKS_2023,
    TM_TRB_2023,
    TM_WINS_2023,
    TM_FG_PCT_2023,
    TM_PT3_PCT_2023,
    TM_FT_PCT_2023
FROM NBA_DB.REPORTS.FCT_TEAM_MASTER_STATS
WHERE YEAR_TM >= 2023

UNION ALL

SELECT
    TEAM_ID,
    TEAM_NAME,
    ABBREVIATION,
    CITY,
    STATE,
    YEAR_FOUNDED,
    ARENA,
    OWNER,
    HEADCOACH,
    YEAR_TM AS SEASON,
    TM_POINTS_2024,
    TM_ASSISTS_2024,
    TM_STEALS_2024,
    TM_BLOCKS_2024,
    TM_TRB_2024,
    TM_WINS_2024,
    TM_FG_PCT_2024,
    TM_PT3_PCT_2024,
    TM_FT_PCT_2024
FROM NBA_DB.REPORTS.FCT_TEAM_MASTER_STATS
WHERE YEAR_TM >= 2024;



CREATE OR REPLACE VIEW NBA_DB.REPORTS.PLAYER_CAREER_STATS AS

SELECT
    PLAYER_ID,
    FULL_NAME,
    FIRSTNAME,
    LASTNAME,
    IS_ACTIVE_PLAYER,
    SCHOOL,
    FROMYEAR,
    DRAFTROUND,
    DRAFTNUMBER,
    BIRTHDATE,
    HEIGHTINCHES,
    BODYWEIGHTLBS,

    TEAMS_PLAYED_FOR,
    SEASONS_PLAYED,
    GAMES_PLAYED,

    CAREER_POINTS,
    CAREER_ASSISTS,
    CAREER_TRB,
    CAREER_DRB,
    CAREER_ORB,
    CAREER_BLOCKS,
    CAREER_TURNOVERS,

    CAREER_FG_PCT,
    CAREER_3PT_PCT,
    CAREER_FT_PCT

FROM NBA_DB.REPORTS.INT_PLAYER_CAREER_STATS;


USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE NBA_DB;
USE SCHEMA REPORTS;

-- To demonstrate the invokation of both a DBT source model with validations in dbt testing AND raw data inclusion of our model views for player data --

CREATE OR REPLACE VIEW player_stats_view AS (
  SELECT d.full_name AS player_name,
       d.is_active,
       a.*,
        CASE WHEN EXTRACT(MONTH FROM a.game_timestamp) <= 7 THEN DATE_PART(YEAR, a.game_timestamp) - 1 ELSE DATE_PART(YEAR, a.game_timestamp) END AS YEAR_SEASON,
       b.abbreviation,
       b.city,
       b.state,
       b.year_founded,
       c.arena,
       c.arenacapacity,
       c.owner,
       c.headcoach,
       c.generalmanager,
       c.instagram AS instagram_link,
       c.facebook AS fb_link,
       c.twitter AS x_link,
FROM ALL_TIME_PLAYERS_STATISTICS a
JOIN NBA_DB.PLAYER_DATA.PLAYER_LIST d
       ON a.player_id = d.id
JOIN NBA_DB.TEAM_DATA.TEAM_LIST  b ON a.player_team_id = b.id
LEFT JOIN TEAM_DETAILS_SOURCE  c
       ON b.id = c.team_id
);


-- Second set for NBA Chatbot (NLP Application) -- 

CREATE OR REPLACE TABLE team_stats_temp AS (
 SELECT TEAMID,
    TEAMNAME,
    CASE WHEN EXTRACT (MONTH FROM game_date) <= 7 THEN DATE_PART(YEAR, game_date) - 1 ELSE DATE_PART(YEAR,game_date) END AS YEAR_TM,
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
    FROM ALLTIME_TEAM_STATISTICS
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
            JOIN NBA_DB.TEAM_DATA.TEAM_LIST b
              ON a.teamid = b.team_id
            LEFT JOIN NBA_DB.TEAM_DATA.TEAM_DETAILS c
               ON b.team_id = c.team_id
                );


-- PULL DATA FROM DBT Views -- 
CREATE OR REPLACE VIEW PLAYER_VIEW AS (
   SELECT FIRSTNAME || ' ' || LASTNAME AS PLAYERNAME, 
   * 
   FROM NBA_DB.PLAYER_DATA.PLAYER_DETAILS 
)

