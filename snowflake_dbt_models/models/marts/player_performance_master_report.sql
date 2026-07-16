-- This model version provides a view of models with JINJA logic if we want to merge player/team data with historical profiles and more categorical information for our AI model --
{% set seasons = [2023,2024,2025] %}
--
--NBA last 3 seasons are used to get the latest player profile stats for ACTIVE players ONLY. 
--
WITH team_mapped AS (
SELECT a.*, 
       b.abbreviation,
       b.city, 
       b.state, 
       b.full_name, 
       b.year_founded
FROM {{ ref('all_time_player_statistics_source') }} a
JOIN {{ ref('team_list_soruce') }} b ON a.player_team_id = b.id
LEFT JOIN {{ ref('team_details_source')}} c
       ON b.id = c.team_id
),

rolled_up_player_perf AS (
       SELECT 
       -- Player name
    {% for ad_id in ad_units %}
       SUM(CASE WHEN product_ad_type = '{{ad_id}}' THEN attributed_sales ELSE 0 END) AS {{ad_id}}_attributed_sales,
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
      0 AS total_sales,
      0 AS units_sold,
      0 AS total_orders,
      0 AS total_sessions,
      0 AS dsp_spend,
      0 AS dsp_sales,
      0 AS shipped_pcogs
FROM all_product_perf
   GROUP BY 1,2,3,4,5,6,7,8,9,10,11
       ),

total_asin_sales AS (
    SELECT c.organization_name,
       c.country_code,
       c.geo_company_name AS company_name,
       c.company_name AS suffixless_company_name,
       c.currency_code,
       --email,
       a.asin,
       p.asin_title,
       p.perpetua_product_id AS product_id,
       p.brand,
       a.geo_company_id,
       a.date AS reporting_date,
      0 AS total_attributed_sales,
      0 AS total_attributed_spend,
      0 AS total_managed_ad_sales,
      0 AS total_managed_ad_spend,
       {% for ad_id in ad_units %}
       0 AS {{ad_id}}_attributed_sales,
    {% endfor %}
       {% for ad_id in ad_units %}
       0 AS {{ad_id}}_attributed_spend,
    {% endfor %}
       0 as clicks,
    {% for ad_id in ad_units %}
       0 AS {{ad_id}}_clicks,
    {% endfor %}
       0 as conversions,
    {% for ad_id in ad_units %}
       0 AS {{ad_id}}_conversions,
    {% endfor %}
       0 AS impressions,
    {% for ad_id in ad_units %}
       0 AS {{ad_id}}_impressions,
    {% endfor %}
      SUM(total_sales) as total_sales,
      SUM(units_sold) as units_sold,
      SUM(orders) as total_orders,
      SUM(sessions) As total_sessions,
      SUM(dsp_spend) AS dsp_spend,
      SUM(dsp_sales) AS dsp_sales,
      SUM(total_shipped_pcogs) AS shipped_pcogs
   FROM {{ref('aggregated_sales_and_traffic_daily_source')}} a
   JOIN {{ ref('perpetua_organization_hierarchy_2026') }} c on a.geo_company_id = c.geo_company_id
    JOIN {{ ref('dim_perpetua_amazon_products')}} p ON a.asin = p.asin AND a.geo_company_id = p.geo_company_id
   WHERE (EXTRACT (year from date) >= EXTRACT(year from CURRENT_DATE())-1)
   GROUP BY 1,2,3,4,5,6,7,8,9,10,11),


SELECT * FROM player_season_totals
UNION ALL
SELECT * FROM
rolled_up_perf
