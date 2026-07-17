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
       b.abbreviation,
       b.city, 
       b.state, 
       b.full_name, 
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
JOIN {{ ref('team_list_soruce') }} b ON a.player_team_id = b.id
LEFT JOIN {{ ref('team_details_source')}} c
       ON b.id = c.team_id
),

rolled_up_player_perf AS (
       SELECT 
       -- Player and Team Dimensions --- 
       full_name, 
       is_active, 
       player_id, 
       teamname, 
       abbreviation,
       city, 
       state, 
       full_name, 
       year_founded,
       arena, 
       arenacapacity, 
       owner, 
       headcoach, 
       generalmanager,
       instagram AS instagram_link, 
       facebook AS fb_link, 
       twitter AS x_link,
       DATE_PART(YEAR, game_timestamp) AS year_int,
       --- Pull primary stats for each season --- 
    {% for i in ad_units %}
       SUM(CASE WHEN DATE_PART(YEAR, game_timestamp) = '{{i}}' THEN points ELSE 0 END) AS {{i}}_points,
    {% endfor %}
       {% for ad_id in ad_units %}
       SUM(CASE WHEN product_ad_type = '{{ad_id}}' THEN attributed_spend ELSE 0 END) AS {{ad_id}}_attributed_spend,
    {% endfor %}
       SUM(clicks) as clicks,
    {% for ad_id in ad_units %}
       SUM(CASE WHEN product_ad_type = '{{ad_id}}' THEN clicks ELSE 0 END) AS {{ad_id}}_clicks,
    {% endfor %}
       SUM(conversions) as conversions,
    {% for ad_id in ad_units %}
       SUM(CASE WHEN product_ad_type = '{{ad_id}}' THEN conversions ELSE 0 END) AS {{ad_id}}_conversions,
    {% endfor %}
       SUM(impressions) AS impressions,
    {% for ad_id in ad_units %}
       SUM(CASE WHEN product_ad_type = '{{ad_id}}' THEN impressions ELSE 0 END) AS {{ad_id}}_impressions,
    {% endfor %}

FROM team_mapped
   GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
       ),

