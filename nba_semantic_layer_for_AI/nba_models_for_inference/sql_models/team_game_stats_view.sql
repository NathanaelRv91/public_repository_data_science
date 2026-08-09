

CREATE OR REPLACE VIEW AS (
  
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
GROUP BY 1,2,3
),

team_mapped AS (
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
FROM team_stats a
            JOIN TEAM_LIST_SOURCE b
              ON a.teamid = b.id
            LEFT JOIN TEAM_DETAILS_SOURCE c
               ON b.id = c.team_id
                ),



)

