/*
  $$ META HEADERS $$
  Importance:::               Client Reporting
  Unique Name:::              mom_targets_and_search_terms_performance
  Location:::                 marts>media>amazon>traffic_reporting
*/


--Search Term Performance for MoM% KPI cards (January 2025 Upgrade)
 SELECT suffixless_company_name,
    geo_company_id,
    country_code,
    match_type,
    email,
    ad_type,
    segment,
    target_term,
    search_term,
    date,
    sum(daily_sales) daily_sales,
    sum(daily_spend) daily_spend,
    sum(conversions) conversions,
    sum(clicks) clicks,
    sum(impressions) impressions,
    --sum(sales_perpetua_attribution) attributed_daily_sales,
    CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(daily_sales),1,0) OVER(Partition By geo_company_id,suffixless_company_name,country_code,match_type,
     email, ad_type, segment, target_term, search_term
  order by extract(day from date), extract(month from date), extract(year from date)) ELSE
    lag(sum(daily_sales),31,0) OVER(Partition By geo_company_id,suffixless_company_name,match_type,
     email, ad_type, segment, target_term, search_term
  order by date)
  END AS last_month_daily_sales,
  CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(daily_spend),1,0) OVER(Partition By geo_company_id,suffixless_company_name,country_code,match_type,
      email, ad_type, segment, target_term, search_term
  order by extract(day from date), extract(month from date), extract(year from date)) ELSE
  lag(sum(daily_spend),31,0) OVER(Partition By geo_company_id,suffixless_company_name,match_type,
      email, ad_type, segment, target_term, search_term
  order by date)
  END AS last_month_daily_spend,
   CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(conversions),1,0) OVER(Partition By geo_company_id,suffixless_company_name,country_code,match_type,
      email, ad_type, segment, target_term, search_term
  order by extract(day from date), extract(month from date), extract(year from date)) ELSE
 lag(sum(conversions),31,0) OVER(Partition By geo_company_id,suffixless_company_name,match_type,
      email, ad_type, segment, target_term, search_term
  order by date)
  END AS last_month_conversions,
  CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(clicks),1,0) OVER(Partition By geo_company_id,suffixless_company_name,country_code,match_type,
      email, ad_type, segment, target_term, search_term
  order by extract(day from date), extract(month from date), extract(year from date)) ELSE
  lag(sum(clicks),31,0) OVER(Partition By geo_company_id,suffixless_company_name,match_type,
      email, ad_type, segment, target_term, search_term
  order by date)
  END AS last_month_clicks,
  CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(impressions),1,0) OVER(Partition By geo_company_id,suffixless_company_name,country_code,match_type,
      email, ad_type, segment, target_term, search_term
  order by extract(day from date), extract(month from date), extract(year from date)) ELSE
   lag(sum(impressions),31,0) OVER(Partition By geo_company_id,suffixless_company_name,match_type,
      email, ad_type, segment, target_term, search_term
  order by date)
  END AS last_month_impressions
FROM {{ ref('reporting_targets_and_search_terms') }}
WHERE date >='2024-01-01'
group by 1,2,3,4,5,6,7,8,9,10
order by 1,2,3,4,5,6,7,8,9,10
