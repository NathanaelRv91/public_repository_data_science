{{config(materialized = 'view') }}


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
  suffixless_company_name,
  geo_company_id,
  email,
  country_code,
  type,
  campaign_name,
  asin,
  title,
  parent_asin,
  perpetua_managed,
  date,
  sum(attributed_sales) daily_sales,
  sum(attributed_spend) daily_spend,
  sum(conversions) conversions,
  sum(clicks) clicks,
  sum(impressions) impressions,
  sum(sales_perpetua_attribution) attributed_daily_sales,
  CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(attributed_sales),1,0) OVER(Partition By geo_company_id,suffixless_company_name,email, country_code,type,
       campaign_name, asin, title, parent_asin,perpetua_managed
  order by extract(day from date), extract(month from date), extract(year from date))
  ELSE
   lag(sum(attributed_sales),31,0) OVER(Partition By geo_company_id,suffixless_company_name,email, country_code,type,
       campaign_name, asin, title, parent_asin,perpetua_managed
  order by date)
   END AS last_month_daily_sales,
     CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(attributed_spend),1,0) OVER(Partition By geo_company_id,suffixless_company_name,email,country_code,type,
       campaign_name, asin, title, parent_asin,perpetua_managed
  order by extract(day from date), extract(month from date), extract(year from date))
  ELSE
lag(sum(attributed_spend),31,0) OVER(Partition By geo_company_id,suffixless_company_name,email, country_code,type,
       campaign_name, asin, title, parent_asin,perpetua_managed
  order by date) END AS
  last_month_daily_spend,
  CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(conversions),1,0) OVER(Partition By geo_company_id,suffixless_company_name,email, country_code,type,
      campaign_name, asin, title, parent_asin,perpetua_managed
  order by extract(day from date), extract(month from date), extract(year from date)) ELSE
lag(sum(conversions),31,0) OVER(Partition By geo_company_id,suffixless_company_name,email, country_code,type,
      campaign_name, asin, title, parent_asin,perpetua_managed
  order by date)
   END AS
  last_month_conversions,
  CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(clicks),1,0) OVER(Partition By geo_company_id,suffixless_company_name,email, country_code,type,
       campaign_name, asin, title, parent_asin,perpetua_managed
  order by extract(day from date), extract(month from date), extract(year from date)) ELSE
  lag(sum(clicks),31,0) OVER(Partition By geo_company_id,suffixless_company_name,email, country_code,type,
       campaign_name, asin, title, parent_asin,perpetua_managed
  order by date)
  END AS
  last_month_clicks,
  CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(impressions),1,0) OVER(Partition By geo_company_id,suffixless_company_name,email,country_code,type,
      campaign_name, asin, title, parent_asin,perpetua_managed
  order by extract(day from date), extract(month from date), extract(year from date)) ELSE
    lag(sum(impressions),31,0) OVER(Partition By geo_company_id,suffixless_company_name,email, country_code,type,
      campaign_name, asin, title, parent_asin,perpetua_managed
  order by date)
  END AS
  last_month_impressions
FROM {{ ref('reporting_ad_unit_perf') }}
WHERE date >='2024-01-01'
group by 1,2,3,4,5,6,7,8,9,10,11
order by 1,2,3,4,5,6,7,8,9,10,11
