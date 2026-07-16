

-- CREATE Model for AI Tools -- 

WITH career_stats AS (
SELECT PLAYER_ID,
PLAYER_TEAM_ID,
YEAR_INT, 
SUM(MIN_PLAYED) AS min_played,
SUM(POINTS) AS points, 
SUM(assists) AS assists, 
SUM(blocks) AS blocks,
SUM(steals) AS steals, 
SUM(FGA) AS fg_attempts, 
DIV0(SUM(FGM),SUM(FGA)) AS fg_pct, 
DIV0(SUM(PT3_FGM),SUM(PT3_ATT)) AS pct_3pt, 
SUM(DRB) AS drb,
SUM(ORB) AS orb, 
SUM(TRB) AS trb, 
COUNT(DISTINCT GAME_ID) AS games_played,
SUM(PF) AS personal_fouls, 
SUM(TOS) AS turnovers, 
LISTAGG(comment) AS all_comments_season
FROM {{ ref('ALL_TIME_PLAYER_STATISTICS_SOURCE')}} 
GROUP BY 1,2,3 ORDER BY 1,2,3
),

team_stats AS (
    SELECT TEAMID, 
    TEAMNAME,
    DATE_PART(YEAR,GAMEDATE) AS YEAR_TM, 
    COUNT(DISTINCT GAMEID) AS team_games_played,
    SUM(REBOUNDSDEFENSIVE) AS team_drb, 
    SUM(REBOUNDSOFFENSIVE) AS team_orb,
    SUM(REBOUNDSTOTAL) AS team_trb,
    SUM(STEALS)AS team_steals, 
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
    FROM {{ref('ALL_TIME_TEAM_STATISTICS_SOURCE')}} 
GROUP BY 1,2,3
)

SELECT a.*,
    b.TEAMNAME, 
    b.team_drb, 
    b.team_orb, 
    b.team_trb, 
    b.team_steals, 
    b.team_blocks, 
    b.team_turnovers, 
    b.team_points, 
    b.team_3pt_fga, 
    b.team_3pt_fgm, 
    b.team_pct_3pt, 
    b.team_fga, 
    b.team_fgm, 
    b.team_pct_fg,
    b.team_fta, 
    b.team_ftm, 
    b.team_pct_ft, 
    b.team_season_wins, 
    DIV0(b.team_season_wins,team_games_played) AS win_pct, 
    FROM career_stats a JOIN team_stats b 
    ON a.YEAR_INT = b.YEAR_TM AND a.PLAYER_TEAM_ID = b.TEAMID
	--WE ONLY Want post-merger data for our training model for forecasting -- 
    WHERE a.YEAR_INT >= 1976;

