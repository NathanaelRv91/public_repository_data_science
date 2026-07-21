{{ config(materialized = 'view', 
  tags = ['team_statistics'], 
  cluster_by = ['TEAMID','YEAR_TM']) }}
  
{% set seasons = [2022,2023,2024,2025,2026] %}
  
WITH team_stats AS (
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
    FROM {{ref('team_all_time_stats_source')}}
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
            JOIN {{ ref('team_list_source') }} b
              ON a.teamid = b.id
            LEFT JOIN {{ ref('team_details_source') }} c
               ON b.id = c.team_id
                ),
team_rolled_up_perf AS (
--- Pull primary stats for each season ---
    SELECT TEAMID            AS team_id,
           TEAMNAME          AS team_name,
           abbreviation,
           city,
           state,
           year_founded,
           arena,
           arenacapacity,
           owner,
           headcoach,
           generalmanager,
           instagram_link,
           fb_link,
           x_link,
           YEAR_TM,
      ----- TEAM SEASON STATS ----
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_points ELSE 0 END) AS tm_points_{{ i }}, {% endfor %}
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_assists ELSE 0 END) AS tm_assists_{{ i }}, {% endfor %}
        {% for i in seasons %}
         SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_steals ELSE 0 END) AS tm_steals_{{ i }}, {% endfor %}
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_blocks ELSE 0 END) AS tm_blocks_{{ i }}, {% endfor %}
        {% for i in seasons %}
         SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_turnovers ELSE 0 END) AS tm_turnovers_{{ i }}, {% endfor %}
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_trb ELSE 0 END) AS tm_trb_{{ i }}, {% endfor %}
        {% for i in seasons %}
         SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_drb ELSE 0 END) AS tm_drb_{{ i }}, {% endfor %}
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_orb ELSE 0 END) AS tm_orb_{{ i }}, {% endfor %}
        {% for i in seasons %}
         SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_3pt_fga ELSE 0 END) AS tm_pt3_fga_{{ i }}, {% endfor %}
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_3pt_fgm ELSE 0 END) AS tm_pt3_fgm_{{ i }}, {% endfor %}
        {% for i in seasons %}
         SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_fta ELSE 0 END) AS tm_fta_{{ i }}, {% endfor %}
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_ftm ELSE 0 END) AS tm_ftm_{{ i }}, {% endfor %}
        {% for i in seasons %}
         SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_fga ELSE 0 END) AS tm_fga_{{ i }}, {% endfor %}
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_fgm ELSE 0 END) AS tm_fgm_{{ i }}, {% endfor %}
        {% for i in seasons %}
           SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_season_wins ELSE 0 END) AS tm_wins_{{ i }}, {% endfor %}
      ---- TEAM SHOOTING PERCENTAGES ----
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_3pt_fgm ELSE 0 END)/SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_3pt_fga END) AS tm_pt3_pct_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_fgm ELSE 0 END)/SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_fga END) AS tm_fg_pct_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_ftm ELSE 0 END)/SUM(CASE WHEN YEAR_TM = '{{i}}' THEN team_fta END) AS tm_ft_pct_{{ i }},
    {% endfor %}
    FROM team_mapped
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)

SELECT * FROM team_rolled_up_perf
