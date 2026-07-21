/*
  $$ META HEADERS $$
  Importance:::               Annual YoY% in total statistics
  Unique Name:::              int_player_season_totals_yoy
  Location:::                 nba_db>reports>views
*/
  {{config(materialized = 'view',
  tag = ['player_statistics'],
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
    TEAM_NAME,
    YEAR_SEASON,
    FB_LINK,
    X_LINK,
    INSTAGRAM_LINK,

    --- Pull primary total stats for YOY by season ---
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN points_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN points_{{i}} ELSE 0 END) AS points_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN assists_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN assists_{{i}} ELSE 0 END) AS assists_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN blocks_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN blocks_{{i}} ELSE 0 END) AS blocks_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN steals_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN steals_{{i}} ELSE 0 END) AS steals_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN trb_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN trb_{{i}} ELSE 0 END) AS trb_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN drb_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN drb_{{i}} ELSE 0 END) AS drb_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN orb_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN orb_{{i}} ELSE 0 END) AS orb_yoy_{{ i }},
        {% endfor %}
    ----- Shooting Statistics -----
     {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fga_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN fga_{{i}} ELSE 0 END) AS fga_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fgm_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN fgm_{{i}} ELSE 0 END) AS fgm_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fta_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN fta_{{i}} ELSE 0 END) AS fta_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN ftm_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN ftm_{{i}} ELSE 0 END) AS ftm_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN ft_pct_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN ft_pct_{{i}} ELSE 0 END) AS ft_pct_yoy_{{ i }},
        {% endfor %}
       {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fg_pct_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN fg_pct_{{i}} ELSE 0 END) AS fg_pct_yoy_{{ i }},
        {% endfor %}
       {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pt3_att_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN pt3_att_{{i}} ELSE 0 END) AS pt3_att_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pt3_fgm_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN pt3_fgm_{{i}} ELSE 0 END) AS pt3_fgm_yoy_{{ i }},
        {% endfor %}
        --- Pull primary per game stats for YOY by season ---
         {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN apg_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN apg_{{i}} ELSE 0 END) AS apg_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN bpg_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN bpg_{{i}} ELSE 0 END) AS bpg_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN drbpg_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN drbpg_{{i}} ELSE 0 END) AS drbpg_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            ROUND((SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN trbpg_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN trbpg_{{i}} ELSE 0 END)),3) AS trbpg_yoy_{{ i }},
        {% endfor %}
        {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN orbpg_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN orbpg_{{i}} ELSE 0 END) AS orbpg_yoy_{{ i }},
        {% endfor %}
       {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN ppg_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN ppg_{{i}} ELSE 0 END) AS ppg_yoy_{{ i }},
        {% endfor %}
       {% for i in seasons %}
            SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN stlpg_{{i}} ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' - 1 THEN stlpg_{{i}} ELSE 0 END) AS stlpg_yoy_{{ i }},
        {% endfor %}

FROM {{ ref('fct_player_master_stats') }}
    GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23
