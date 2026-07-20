/*
  $$ META HEADERS $$
  Importance:::               Perpetua Base Reporting
  Query URL or File:::        marts>media>amazon>asin_performance
  Unique Name:::              mom_total_sales_performance
*/

 SELECT suffixless_company_name,
     geo_company_id,
     country_code,
     email,
     is_vendor,
     asin,
     asin_title,
     parent_asin,
     date,
     sum(sales) AS sales,
     sum(spend) AS spend,
     sum(conversions) AS conversions,
     sum(clicks) AS clicks,
     sum(impressions) as impressions,
     CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(sales),1,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by extract(day from date), extract(month from date), extract(year from date))
 ELSE
  lag(sum(sales),31,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by date)
  END as last_month_sales,
  CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(spend),1,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by extract(day from date), extract(month from date), extract(year from date))
    ELSE lag(sum(spend),31,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by date)
  END AS last_month_spend,
        CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(conversions),1,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by extract(day from date), extract(month from date), extract(year from date))
    ELSE lag(sum(conversions),31,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by date)
  END AS last_month_conversions,
      CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(clicks),1,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by extract(day from date), extract(month from date), extract(year from date))
    ELSE lag(sum(clicks),31,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by date)
  END AS last_month_clicks,
      CASE WHEN EXTRACT(MONTH FROM date) != 1 THEN
  lag(sum(impressions),1,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by extract(day from date), extract(month from date), extract(year from date))
    ELSE lag(sum(impressions),31,0) OVER(Partition By geo_company_id,suffixless_company_name,
     country_code, email, is_vendor, asin, asin_title, parent_asin
  order by date)
  END AS last_month_impressions
FROM {{ ref('reporting_total_sales') }}
WHERE date >='2024-01-01'
group by 1,2,3,4,5,6,7,8,9
order by 1,2,3,4,5,6,7,8,9
