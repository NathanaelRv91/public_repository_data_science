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
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN points_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN points_{{i}} AS points_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN assists_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN assists_{{i}} AS assists_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN blocks_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN blocks_{{i}} AS blocks_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN steals_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN steals_{{i}} AS steals_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN trb_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN trb_{{i}} AS trb_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN drb_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN drb_{{i}} AS drb_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN trb_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN trb_{{i}} AS trb_yoy_{{ i }},
        {% endfor %}
    ----- Shooting Statistics -----
     {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fga_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN fga_{{i}} AS fga_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fgm_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN fgm_{{i}} AS fgm_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN ft_pct_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN ft_pct_{{i}} AS ft_pct_yoy_{{ i }},
        {% endfor %}
       {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pt3_att_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN pt3_att_{{i}} AS pt3_att_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pt3_fgm_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = {{i}} - 1))-1,3) THEN pt3_fgm_{{i}} AS pt3_fgm_yoy_{{ i }},
        {% endfor %}

FROM {{ ref('fct_player_master_stats') }}
group by 1,2,3,4,5,6,7,8,9,10,11
order by 1,2,3,4,5,6,7,8,9,10,11
