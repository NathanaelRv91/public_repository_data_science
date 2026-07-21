/*
  $$ META HEADERS $$
  Importance:::               Client Reporting
  Unique Name:::              reporting_mom_ad_unit_performance
  Location:::                 marts>media>amazon>sponsored_ads
*/

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
   FROMYEAR AS FIRST_SEASON, 
   FULL_NAME, 
   HEADCOACH AS COACH_NAME, 
   GENERALMANAGER AS GM_NAME, 
   OWNER, 
   IS_ACTIVE_PLAYER, 
   LASTNAME, 
   PLAYER_ID, 
   SCHOOL, 
   TEAMNAME, 
   YEAR_SEASON, 
   FB_LINK, 
   X_LINK, 
   INSTAGRAM_LINK, 
  --CALCULATE YOY VALUES -- 
   
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
FROM {{ ref('fct_player_master_stats') }}
WHERE date >='2024-01-01'
group by 1,2,3,4,5,6,7,8,9,10,11
order by 1,2,3,4,5,6,7,8,9,10,11
