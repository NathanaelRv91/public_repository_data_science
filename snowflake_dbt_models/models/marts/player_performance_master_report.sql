-- This model version provides a view of models with JINJA logic if we want to merge player/team data with historical profiles and more categorical information for our AI model --
{% set seasons = [2022,2023,2024,2025,2026] %}
--
--NBA last 3 seasons are used to get the latest player profile stats for ACTIVE players ONLY.
-- This report does NOT include player vs team seasonal totals for the analysis. The player pct of team totals can be found in the 'int_player_team_stats' -- 
--
WITH team_mapped AS (
SELECT d.full_name
       d.is_active, 
       a.*, 
        CASE WHEN DATE_PART(MONTH, a.game_timestamp) <= 7 THEN DATE_PART(YEAR, a.game_timestamp) - 1 ELSE DATE_PART(YEAR, a.game_timestamp) END AS YEAR_INT,
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
FROM {{ ref('all_time_player_statistics_source') }} a
JOIN {{ ref('player_list_source')}} d 
       ON a.player_id = b.id
JOIN {{ ref('team_list_source') }} b ON a.player_team_id = b.id
LEFT JOIN {{ ref('team_details_source')}} c
       ON b.id = c.team_id
),

rolled_up_player_perf AS (
       SELECT 
       -- Player and Team Dimensions --- 
       full_name AS player_name, 
       is_active, 
       player_id, 
       player_team_name AS team_name, 
       abbreviation,
       city, 
       state, 
       year_founded,
       arena, 
       arenacapacity, 
       owner, 
       headcoach, 
       generalmanager,
       instagram AS instagram_link, 
       facebook AS fb_link, 
       twitter AS x_link,
       YEAR_INT,
       --- Pull primary stats for each season --- 
    {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN points ELSE 0 END) AS {{i}}_points,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN assists ELSE 0 END) AS {{i}}_assists,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN blocks ELSE 0 END) AS {{i}}_blocks,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN fga ELSE 0 END) AS {{i}}_fga,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN fgm ELSE 0 END) AS {{i}}_fgm,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN pt3_att ELSE 0 END) AS {{i}}_pt3_att,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN pt3_fgm ELSE 0 END) AS {{i}}_pt3_fgm,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN trb ELSE 0 END) AS {{i}}_trb,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN drb ELSE 0 END) AS {{i}}_drb,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN or orb ELSE 0 END) AS {{i}}_orb,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN pf ELSE 0 END) AS {{i}}_pf,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN tos ELSE 0 END) AS {{i}}_turnovers,
    {% endfor %}
       -- Shooting Percentages -- 
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN fgm ELSE 0 END)/COUNT(CASE WHEN YEAR_INT = '{{i}}' THEN fga END) AS {{i}}_fg_pct,
    {% endfor %}
            {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN ftm ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN fta END) AS {{i}}_ft_pct,
    {% endfor %}
           {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN pt3_fgm ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN pt3_att END) AS {{i}}_pt3_pct,
    {% endfor %}
       -- PER GAME STATS
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN points ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN 1 END) AS {{i}}_ppg,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN assists ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN 1 END) AS {{i}}_apg,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN blocks ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN 1 END) AS {{i}}_bpg,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN steals ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN 1 END) AS {{i}}_stlpg,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN trb ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN 1 END) AS {{i}}_trbpg,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN drb ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN 1 END) AS {{i}}_drbpg,
    {% endfor %}
        {% for i in seasons %}
       SUM(CASE WHEN YEAR_INT = '{{i}}' THEN orb ELSE 0 END)/SUM(CASE WHEN YEAR_INT = '{{i}}' THEN 1 END) AS {{i}}_orbpg,
    {% endfor %}
 
FROM team_mapped
       WHERE is_active = 1
   GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
       ),

-- All of our player sources (list, details, career_accolades) we use to build the full end-user plofiles have conforming dimensions on the primary key PLAYER_ID --
player_profiles AS (
SELECT 
    birthdate,
    bodyweightlbs,
    heightinches,
    firstname,
    lastname,
    firstname || ' ' || lastname AS full_name,
    CASE WHEN TOYEAR > 2025 THEN 'ACTIVE' ELSE 'RETIRED' END AS is_active_player,
    school,
    fromyear,
    draftround,
    draftnumber,
    jersey
FROM {{ ref('player_details_source')}} 
WHERE toyear >= 2026
) 


