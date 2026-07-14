-- This model version provides a view of models with JINJA logic if we want to merge total perf with ad_unit specific data --
{% set ad_units = ["sponsored_brands","sponsored_display","sponsored_products"] %}
--
--PERPETUA Combined Product Performance for all Perpetua Geo Companies
--
WITH augmented_exchange_rates AS (
SELECT country_code,
       from_currency,
       to_currency,
       exchange_rate,
       date
FROM {{ ref('exchange_rates_source') }}
JOIN {{ ref('country_currency_mapping') }} ON from_currency = currency_code
WHERE to_currency = "USD"
),
all_product_perf AS (
SELECT
    *,
     'sponsored_brands' AS product_ad_type
FROM {{ ref('perpetua_amazon_sb_product_performance_basic') }}

UNION ALL
SELECT
    *,
    'sponsored_display' AS product_ad_type
FROM {{ ref('perpetua_amazon_sd_product_performance_basic')}}

UNION ALL
SELECT
    *,
    'sponsored_products' AS product_ad_type
FROM {{ ref('perpetua_amazon_sp_product_performance_basic') }}
),

rolled_up_perf AS (
       SELECT organization_name,
       country_code,
       company_name,
       suffixless_company_name,
       currency_code,
       --email,
       asin,
       asin_title,
       product_id,
       brand,
       geo_company_id,
       reporting_date,
       SUM(attributed_sales) AS total_attributed_sales,
       SUM(attributed_spend) AS total_attributed_spend,
       SUM(CASE WHEN perpetua_managed = True THEN attributed_sales ELSE 0 END) as total_managed_ad_sales,
       SUM(CASE WHEN perpetua_managed = True THEN attributed_spend ELSE 0 END) as total_managed_ad_spend,

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

perpetua_managed1 AS (
SELECT DISTINCT asin, geo_company_id,
perpetua_managed
FROM {{ref('perpetua_amazon_combined_product_performance_basic')}}
),

perpetua_managed2 AS (
  SELECT *,
  RANK() OVER(PARTITION by ASIN, geo_company_id ORDER BY perpetua_managed DESC) as rank_product
  FROM perpetua_managed1
),

perpetua_managed AS (
       SELECT * FROM perpetua_managed2 WHERE rank_product = 1
)

SELECT * FROM total_asin_sales
UNION ALL
SELECT * FROM
rolled_up_perf
