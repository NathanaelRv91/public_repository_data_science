USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE NBA_DB;
USE SCHEMA REPORTS;

-- To demonstrate the invokation of both a DBT source model with validations in dbt testing AND raw data inclusion of our model views for player data --

CREATE VIEW player_stats_view AS (
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
FROM ALL_TIME_PLAYER_STATISTICS a
JOIN NBA_DB.PLAYER_DATA.PLAYER_LIST d
       ON a.player_id = d.id
JOIN NBA_DB.TEAM_DATA.TEAM_LIST  b ON a.player_team_id = b.id
LEFT JOIN TEAM_DETAILS_SOURCE  c
       ON b.id = c.team_id
  FROM ALL_TIME_PLAYERS_STATISTICS
) 



