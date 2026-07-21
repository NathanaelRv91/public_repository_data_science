-- This model version provides a view of models with JINJA logic if we want to merge player/team data with historical profiles and more categorical information for our AI model --
{{ config(materialized = 'view',
       tags = ['player_statistics']) }}
{% set seasons = [2022,2023,2024,2025,2026] %}
--
--NBA last 3 seasons are used to get the latest player profile stats for ACTIVE players ONLY.
-- This report does NOT include player vs team seasonal totals for the analysis. The player pct of team totals can be found in the 'int_player_team_stats' --
--
WITH team_mapped AS (
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
FROM {{ ref('player_all_time_stats_source') }} a
JOIN {{ ref('player_list_source')}} d
       ON a.player_id = d.id
JOIN {{ ref('team_list_source') }} b ON a.player_team_id = b.id
LEFT JOIN {{ ref('team_details_source')}} c
       ON b.id = c.team_id
),
-- All of our player sources (list, details, career_accolades) we use to build the full end-user plofiles have conforming dimensions on the primary key PLAYER_ID --
rolled_up_player_perf AS (SELECT
                              -- Player and Team Dimensions ---
                              player_name,
                              is_active,
                              player_id,
                              player_team_name                                         AS team_name,
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
                              YEAR_SEASON,
                              --- Pull primary stats for each season ---
                              {% for i in seasons %}
                              SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN points ELSE 0 END) AS points_{{ i }},
                                {% endfor %}
                           {% for i in seasons %}
                        SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN assists ELSE 0 END) AS assists_{{ i }},
                            {% endfor %}
                                {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN blocks ELSE 0 END) AS blocks_{{ i }},
    {% endfor %}
    {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN steals ELSE 0 END) AS steals_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fga ELSE 0 END) AS fga_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fgm ELSE 0 END) AS fgm_{{ i }},
    {% endfor %}
             {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fta ELSE 0 END) AS fta_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN ftm ELSE 0 END) AS ftm_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pt3_att ELSE 0 END) AS pt3_att_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pt3_fgm ELSE 0 END) AS pt3_fgm_{{ i }},
    {% endfor %}
    {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN trb ELSE 0 END) AS trb_{{ i }},
        {% endfor %}
    {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN drb ELSE 0 END) AS drb_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN orb ELSE 0 END) AS orb_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pf ELSE 0 END) AS personal_fouls_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN tos ELSE 0 END) AS turnovers_{{ i }},
    {% endfor %}
       -- Shooting Percentages --
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fgm ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fga END) AS fg_pct_{{ i }},
    {% endfor %}
            {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN ftm ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN fta END) AS ft_pct_{{ i }},
    {% endfor %}
           {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pt3_fgm ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN pt3_att END) AS pt3_pct_{{ i }},
    {% endfor %}
       -- PER GAME STATS
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN points ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN 1 END) AS ppg_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN assists ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN 1 END) AS apg_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN blocks ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN 1 END) AS bpg_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN steals ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN 1 END) AS stlpg_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN trb ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN 1 END) AS trbpg_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN drb ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN 1 END) AS drbpg_{{ i }},
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN orb ELSE 0 END)/SUM(CASE WHEN YEAR_SEASON = '{{i}}' THEN 1 END) AS orbpg_{{ i }},
    {% endfor %}

FROM team_mapped
    WHERE is_active = 1
GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17
                 ),
-- All of our player sources (list, details, career_accolades) we use to build the full end-user plofiles have conforming dimensions on the primary key PLAYER_ID --
player_profiles AS (
SELECT
    personid,
    birthdate,
    bodyweightlbs,
    heightinches,
    firstname,
    lastname,
    firstname || ' ' || lastname AS full_name,
    CASE WHEN TOYEAR > 2025 THEN 'ACTIVE' ELSE 'RETIRED' END AS is_active_player,
    school,
    fromyear,
    toyear,
    draftround,
    draftnumber,
    jersey,
    guard,
    forward,
    center
FROM {{ ref('player_details_source')}}
WHERE toyear >= 2026
)

SELECT a.*,
    b.birthdate,
    b.bodyweightlbs,
    b.heightinches,
    b.firstname,
    b.lastname,
    b.firstname || ' ' || b.lastname AS full_name,
    CASE WHEN b.TOYEAR > 2025 THEN 'ACTIVE' ELSE 'RETIRED' END AS is_active_player,
    b.school,
    b.fromyear,
    b.draftround,
    b.draftnumber,
    b.jersey,
    CASE WHEN b.guard = 1 THEN 'YES' ELSE 'NO' END AS is_guard,
    CASE WHEN b.forward = 1 THEN 'YES' ELSE 'NO' END AS is_forward,
    CASE WHEN b.center = 1 THEN 'YES' ELSE 'NO' END AS is_center,
    CASE WHEN ((b.guard = 1 AND b.forward = 1) OR (b.guard = 1 AND b.center = 1) OR (b.forward = 1 AND b.center = 1)) THEN 'YES' ELSE 'NO' END AS plays_multiple_positions

    FROM rolled_up_player_perf a
        JOIN player_profiles b on a.player_id = b.personid

