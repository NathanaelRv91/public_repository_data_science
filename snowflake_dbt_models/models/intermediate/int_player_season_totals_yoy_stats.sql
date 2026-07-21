/*
  $$ META HEADERS $$
  Importance:::               Annual YoY% in total statistics
  Unique Name:::              int_player_season_totals_yoy
  Location:::                 nba_db>reports>views
*/

  {{config(materialized = 'view', 
  tag = ['player_total_stats'], 
  cluster_by = ['team_id','player_id','YEAR_SEASON'])}}

  {% set seasons = [2023,2024,2025,2026] %}


 SELECT
  ABBREVIATION, 
  ARENA,
    BIRTHDATE, 
    BODYWEIGHTLBS AS BW_LBS, 
    HEIGHTINCHES AS HT_IN, 
    CITY, 
    DRAFTNUMBER, 
    DRAFTROUND, 
    FIRSTNAME, 
    FULL_NAME, 
    LASTNAME, 
    FROMYEAR AS FIRST_SEASON, 
    HEADCOACH AS COACH_NAME, 
    GENERALMANAGER AS GM_NAME, 
    OWNER, 
    IS_ACTIVE_PLAYER, 
    PLAYER_ID, 
    SCHOOL, 
    TEAMNAME, 
    YEAR_SEASON, 
    FB_LINK, 
    X_LINK, 
    INSTAGRAM_LINK,

    --- Pull primary stats for YOY by season ---
                              {% for i in seasons %}
                              SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN points ELSE 0 END) AS points_{{ i }},
                                {% endfor %}
                           {% for i in seasons %}
                        SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN assists ELSE 0 END) AS assists_{{ i }},
                            {% endfor %}
                                {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN blocks ELSE 0 END) AS blocks_{{ i }},


FROM {{ ref('reporting_ad_unit_perf') }}
group by 1,2,3,4,5,6,7,8,9,10,11
order by 1,2,3,4,5,6,7,8,9,10,11
