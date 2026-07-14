
## merge our all time stats into our career profiles ## 
create or replace view PRNG_STAGE.PUBLIC.PRODUCTCATEGORYDATA(
	MARKETNAME,
	RETAILERNAME,
	BANNERNAME,
	CHANNELNAME,
	FORMATNAME,
	YEAR,
	PRODUCTCATEGORY,
	SPLIT
) as
SELECT
        r.marketname,
        r.retailername,
        r.bannername,
        r.channelname,
        r.formatname,
        r.year,
        IFNULL(b.productcategory, IFNULL(y.productcategory, IFNULL(m.productcategory, d.productcategory))) productcategory,
        IFNULL(b.percentage_split, IFNULL(y.percentage_split, IFNULL(m.percentage_split, d.percentage_split)))/100 split

      FROM
        PRNG.PUBLIC.PRNGRETAILERDATA r
      LEFT OUTER JOIN PRNG.PUBLIC.prngproductcategory_banner b on
        b.retailer = r.retailername and b.banner = r.bannername and b.format =  r.formatname and b.channel = r.channelname and b.market = r.marketname and b.year = YEAR(r.YEAR)
      LEFT OUTER JOIN PRNG.PUBLIC.prngproductcategory_year y on
        y.format =  r.formatname and y.channel = r.channelname and y.market = r.marketname and y.year = YEAR(r.YEAR) and b.productcategory is null
      LEFT OUTER JOIN PRNG.PUBLIC.prngproductcategory_market m on
        m.format =  r.formatname and m.channel = r.channelname and m.market = r.marketname and b.productcategory is null and y.productcategory is null
      LEFT OUTER JOIN PRNG.PUBLIC.prngproductcategory_defaults d on
        d.format =  r.formatname and d.channel = r.channelname and b.productcategory is null and y.productcategory is null and m.productcategory is null
-- WE use the same model view from POWER_BI.PRODUCTCATEGORYDATA -- 
          WHERE r.MARKETNAME = 'United States'
        AND DATE_PART(YEAR,r.YEAR) BETWEEN 2024 AND 2031
        AND r.FORMATNAME IN ('Pureplay-1P','Pureplay-3P','Drive','Social Commerce','Omnichannel-1P','Omnichannel-3P')
        AND r.CHANNELNAME IN ('Mass Merchandise','Department Stores','Beauty Specialists','Pharma & Health','Cash & Carry/Club','Hyper-Stores','Supermarkets & Neighbourhood Stores')      
;
