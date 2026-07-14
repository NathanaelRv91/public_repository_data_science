# Snowpark Model that runs server-side from calculated market profiles ## 
import pandas as pd
import numpy as np 
from datetime import date
from datetime import time 
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector as sconn

from snowflake.snowpark.context import get_active_session
session = get_active_session()

product_category_channel = session.table("PRODUCT_DB.PUBLIC.SUBCATEGORY_PROFILE")
product_category_channel = product_category_channel.to_pandas()
banner_category_channel = session.table("PRODUCT_DB.PUBLIC.SUBCATEGORY_BANNER")
banner_category_channel = banner_category_channel.to_pandas()

online_retailers = session.table("PRODUCT_DB.PUBLIC.RETAILERDATA")
online_retailers = online_retailers.to_pandas()
online_retailers = online_retailers[online_retailers.MARKETNAME == 'United States']
online_retailers = online_retailers[online_retailers.CHANNELNAME.isin(['Mass Merchandise','Cash & Carry/Club','Department Stores','Hyper-Stores','Other Non-Food Specialists','Pharma & Health','Supermarkets & Neighbourhood Stores',
                'Convenience','Discount','Beauty Specialists'])]
online_retailers = online_retailers[online_retailers.FORMATNAME.isin(['Pureplay-1P','Pureplay-3P','Drive','Social Commerce','Omnichannel-1P','Omnichannel-3P'])]
online_retailers = online_retailers[['MARKETNAME', 'RETAILERNAME', 'BANNERNAME', 'CHANNELNAME', 'FORMATNAME',
       'YEAR', 'CURRENCYCODE', 'NETSALES', 'GROSSSALES', 'STORES',
       'AVERAGESELLINGSPACE', 'RETAILERID',
       'BANNERID']]
online_retailers['YEAR_int'] = pd.to_datetime(online_retailers['YEAR'])
online_retailers['YEAR_int'] = online_retailers['YEAR_int'].dt.year
online_retailers = online_retailers[online_retailers.YEAR_int <= 2031]
online_retailers = online_retailers[online_retailers.YEAR_int >= 2024]
online_retailers = online_retailers[online_retailers.NETSALES > 0]
online_retailers.reset_index(inplace = True)
online_retailers.sort_values(by = ['BANNERNAME','FORMATNAME','YEAR'], inplace = True)
online_retailers['ly_netsales'] = online_retailers['NETSALES'].shift(1, fill_value = 0)

for i in range(len(online_retailers)):
    if online_retailers.loc[i,'YEAR_int'] > 2024:
        online_retailers.loc[i,'NETSALES_yoy_retailer'] = ((online_retailers.loc[i,'NETSALES']/online_retailers.loc[i,'ly_netsales'])-1).round(6)
    else:
        pass
online_retailers = online_retailers[online_retailers.BANNERNAME != 'Vitacost.com']
online_retailers = online_retailers[online_retailers.BANNERNAME != 'PetCareRx.com']

##Add Grocery Default & Banner Splits to the model##
banner_splits = session.table("PRODUCT_DB.PUBLIC.CATEGORYDATA")
#banner_splits = sub.pull_powerbi_splits()
banner_splits = banner_splits.to_pandas()
banner_splits['YEAR_int'] = pd.to_datetime(banner_splits['YEAR'])
banner_splits['YEAR_int'] = banner_splits['YEAR_int'].dt.year
banner_splits = banner_splits[banner_splits.PRODUCTCATEGORY.isin(['Household care','Pet care','Health & Beauty','Edible grocery'])]
online_retailers = pd.merge(online_retailers, banner_splits,how = 'inner', left_on = ['MARKETNAME','RETAILERNAME','BANNERNAME','CHANNELNAME','FORMATNAME','YEAR_int'],right_on = ['MARKETNAME','RETAILERNAME','BANNERNAME','CHANNELNAME','FORMATNAME','YEAR_int'])
online_retailers.reset_index(inplace = True)
online_retailers.rename(columns = {"SPLIT":"PERCENTAGE_SPLIT"},inplace = True)
online_retailers.sort_values(by = ['BANNERNAME','FORMATNAME','PRODUCTCATEGORY','YEAR_int'], inplace = True)

for i in range(len(online_retailers)):
    if online_retailers.loc[i,'NETSALES'] > 0:
        online_retailers.loc[i, 'CATEGORY_NETSALES'] = online_retailers.loc[i, 'NETSALES'] * (
                    online_retailers.loc[i, 'PERCENTAGE_SPLIT'])
online_retailers = online_retailers[online_retailers.BANNERNAME != 'Vitacost.com']
online_retailers = online_retailers[online_retailers.BANNERNAME != 'PetCareRx.com']
online_retailers['ly_categorysales'] = online_retailers['CATEGORY_NETSALES'].shift(1, fill_value = 0)
online_retailers['CATEGORY_yoy_retailer'] = (online_retailers['CATEGORY_NETSALES']/online_retailers['ly_categorysales']) -1
## Setup Full model Build by Brining in BASE Profile for Data ##
online_retailers.drop(columns = ['index'], inplace = True)
subcategory_model = pd.merge(online_retailers, product_category_channel, how = 'inner',left_on = ['CHANNELNAME','FORMATNAME','PRODUCTCATEGORY'], right_on = ['CHANNELNAME','FORMATNAME','MAIN_CATEGORY'])

## THIS will be PRNG_STAGE.PUBLIC.PRNGSUBCATEGORY_BANNER ##
mass_merch_model = pd.merge(subcategory_model,banner_category_channel, how = 'left', left_on = ['MARKETNAME_x','RETAILERNAME','BANNERNAME','CHANNELNAME','FORMATNAME','PRODUCTCATEGORY','RI_SUBCATEGORY'], right_on = ['MARKETNAME','RETAILERNAME','BANNERNAME','CHANNELNAME','FORMATNAME','MAIN_CATEGORY','RI_SUBCATEGORY'])
mass_merch_model.reset_index(inplace = True)
for i in range(len(mass_merch_model)):
    mass_merch_model.loc[i,'PCT_TOTAL'] = mass_merch_model.loc[i,'SUBCATEGORY_PCT'] if pd.notna(mass_merch_model.loc[i, 'SUBCATEGORY_PCT']) \
 else mass_merch_model.loc[i, 'PCT_TOTAL']

for i in range(len(mass_merch_model)):
    mass_merch_model.loc[i,'TOTAL_YOY'] = mass_merch_model.loc[i,'SUBCATEGORY_YOY'] if pd.notna(mass_merch_model.loc[i, 'SUBCATEGORY_YOY']) \
 else mass_merch_model.loc[i, 'TOTAL_YOY']

mass_merch_model.sort_values(by = ['BANNERNAME','FORMATNAME','PRODUCTCATEGORY','YEAR_int'], inplace = True)

for i in range(len(mass_merch_model)):
    if mass_merch_model.loc[i, 'BANNERNAME'] == 'Amazon.com':
        if mass_merch_model.loc[i, 'FORMATNAME'] =='Pureplay-1P':
            mass_merch_model.loc[i, 'PCT_TOTAL'] = mass_merch_model.loc[i, 'PCT_1P']
            if mass_merch_model.loc[i, 'PRODUCTCATEGORY'] !='Edible grocery':
                mass_merch_model.loc[i, 'TOTAL_YOY'] = mass_merch_model.loc[i, 'YOY_1P']
        else:
            mass_merch_model.loc[i, 'PCT_TOTAL'] = mass_merch_model.loc[i, 'PCT_3P']
            if mass_merch_model.loc[i, 'PRODUCTCATEGORY'] !='Edible grocery':
                mass_merch_model.loc[i, 'TOTAL_YOY'] = mass_merch_model.loc[i, 'YOY_3P']
    else:
        pass

for i in range(len(mass_merch_model)):
    if mass_merch_model.loc[i,'NETSALES'] > 0:
        mass_merch_model.loc[i,'SUBCATEGORY_NETSALES'] = (mass_merch_model.loc[i,'NETSALES'] * (mass_merch_model.loc[i,'PERCENTAGE_SPLIT'] * mass_merch_model.loc[i,'PCT_TOTAL']))
        mass_merch_model.loc[i,'growth_multiplier'] = mass_merch_model.loc[i,'TOTAL_YOY'] * mass_merch_model.loc[i,'PCT_TOTAL']
    else:
        pass

mass_merch_model.sort_values(by = ['PRODUCTCATEGORY','BANNERNAME','FORMATNAME','YEAR_int'], inplace = True)

## Separate Base Model from Main Model ##
mass_merch_base = mass_merch_model[mass_merch_model.YEAR_int == 2024]
mass_merch_base = mass_merch_base.groupby(['BANNERNAME','FORMATNAME','PRODUCTCATEGORY']).growth_multiplier.sum()
mass_merch_base = pd.DataFrame(mass_merch_base)
mass_merch_base.reset_index(inplace = True)
mass_merch_base = mass_merch_base[['BANNERNAME','FORMATNAME','PRODUCTCATEGORY','growth_multiplier']]
mass_merch_base.columns = ['BANNER','FORMAT','BASE_CATEGORY','growth_share_annual']
mass_merch_model = mass_merch_model[['MARKETNAME_x','RETAILERNAME','BANNERNAME','CHANNELNAME','FORMATNAME','YEAR_x','NETSALES','ly_netsales','NETSALES_yoy_retailer',
                                     'PRODUCTCATEGORY','RI_SUBCATEGORY','YEAR_int','PCT_TOTAL','TOTAL_YOY','PERCENTAGE_SPLIT',
                                     'SUBCATEGORY_NETSALES','CATEGORY_NETSALES','growth_multiplier','CATEGORY_yoy_retailer']]

mass_merch_model = pd.merge(mass_merch_model,mass_merch_base, how = 'left', left_on = ['BANNERNAME','FORMATNAME','PRODUCTCATEGORY'], right_on = ['BANNER','FORMAT','BASE_CATEGORY'])
mass_merch_model.reset_index(inplace = True)

for i in range(len(mass_merch_model)):
    if mass_merch_model.loc[i,'PRODUCTCATEGORY'] == 'Household care':
        if mass_merch_model.loc[i,'YEAR_int'] == 2025:
            mass_merch_model.loc[i,'sales_added_share'] = ((mass_merch_model.loc[i,'growth_multiplier']) / (mass_merch_model.loc[i,'growth_share_annual']))
            mass_merch_model.loc[i, 'cat_sales_diff'] = ((mass_merch_model.loc[i, 'CATEGORY_NETSALES']) - (mass_merch_model.loc[i - 9, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'subcategory_sales_diff'] = ((mass_merch_model.loc[i, 'cat_sales_diff']) * (mass_merch_model.loc[i, 'sales_added_share']))
            mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES'] = (
                        (mass_merch_model.loc[i - 9, 'SUBCATEGORY_NETSALES']) + (mass_merch_model.loc[i, 'subcategory_sales_diff']))
            mass_merch_model.loc[i, 'PCT_TOTAL'] = (
                        (mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'TOTAL_YOY'] = (
                ((mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i - 9, 'SUBCATEGORY_NETSALES'])) -1)
            mass_merch_model.loc[i, 'growth_multiplier'] = (
                    (mass_merch_model.loc[i - 9, 'PCT_TOTAL']) * (
                    mass_merch_model.loc[i, 'TOTAL_YOY']))
    elif mass_merch_model.loc[i,'PRODUCTCATEGORY'] == 'Pet care':
        if mass_merch_model.loc[i,'YEAR_int'] == 2025:
            mass_merch_model.loc[i,'sales_added_share'] = ((mass_merch_model.loc[i,'growth_multiplier']) / (mass_merch_model.loc[i,'growth_share_annual']))
            mass_merch_model.loc[i, 'cat_sales_diff'] = ((mass_merch_model.loc[i, 'CATEGORY_NETSALES']) - (mass_merch_model.loc[i - 6, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'subcategory_sales_diff'] = ((mass_merch_model.loc[i, 'cat_sales_diff']) * (mass_merch_model.loc[i, 'sales_added_share']))
            mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES'] = (
                        (mass_merch_model.loc[i - 6, 'SUBCATEGORY_NETSALES']) + (mass_merch_model.loc[i, 'subcategory_sales_diff']))
            mass_merch_model.loc[i, 'PCT_TOTAL'] = (
                        (mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'TOTAL_YOY'] = (
                ((mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i - 6, 'SUBCATEGORY_NETSALES'])) -1)
            mass_merch_model.loc[i, 'growth_multiplier'] = (
                    (mass_merch_model.loc[i - 6, 'PCT_TOTAL']) * (
                    mass_merch_model.loc[i, 'TOTAL_YOY']))
    elif mass_merch_model.loc[i,'PRODUCTCATEGORY'] == 'Health & Beauty':
        if mass_merch_model.loc[i,'YEAR_int'] == 2025:
            mass_merch_model.loc[i,'sales_added_share'] = ((mass_merch_model.loc[i,'growth_multiplier']) / (mass_merch_model.loc[i,'growth_share_annual']))
            mass_merch_model.loc[i, 'cat_sales_diff'] = ((mass_merch_model.loc[i, 'CATEGORY_NETSALES']) - (mass_merch_model.loc[i - 11, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'subcategory_sales_diff'] = ((mass_merch_model.loc[i, 'cat_sales_diff']) * (mass_merch_model.loc[i, 'sales_added_share']))
            mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES'] = (
                        (mass_merch_model.loc[i - 11, 'SUBCATEGORY_NETSALES']) + (mass_merch_model.loc[i, 'subcategory_sales_diff']))
            mass_merch_model.loc[i, 'PCT_TOTAL'] = (
                        (mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'TOTAL_YOY'] = (
                ((mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i - 11, 'SUBCATEGORY_NETSALES'])) -1)
            mass_merch_model.loc[i, 'growth_multiplier'] = (
                    (mass_merch_model.loc[i - 11, 'PCT_TOTAL']) * (
                    mass_merch_model.loc[i, 'TOTAL_YOY']))
    elif mass_merch_model.loc[i,'PRODUCTCATEGORY'] == 'Edible grocery':
        if mass_merch_model.loc[i,'YEAR_int'] == 2025:
            mass_merch_model.loc[i,'sales_added_share'] = ((mass_merch_model.loc[i,'growth_multiplier']) / (mass_merch_model.loc[i,'growth_share_annual']))
            mass_merch_model.loc[i, 'cat_sales_diff'] = ((mass_merch_model.loc[i, 'CATEGORY_NETSALES']) - (mass_merch_model.loc[i-13, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'subcategory_sales_diff'] = ((mass_merch_model.loc[i, 'cat_sales_diff']) * (mass_merch_model.loc[i, 'sales_added_share']))
            mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES'] = (
                        (mass_merch_model.loc[i - 13, 'SUBCATEGORY_NETSALES']) + (mass_merch_model.loc[i, 'subcategory_sales_diff']))
            mass_merch_model.loc[i, 'PCT_TOTAL'] = (
                        (mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'TOTAL_YOY'] = (
                ((mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i - 13, 'SUBCATEGORY_NETSALES'])) -1)
            mass_merch_model.loc[i, 'growth_multiplier'] = (
                    (mass_merch_model.loc[i-13, 'PCT_TOTAL']) * (
                    mass_merch_model.loc[i, 'TOTAL_YOY']))
    else:
        pass

for i in range(len(mass_merch_model)):
    if mass_merch_model.loc[i, 'PRODUCTCATEGORY'] == 'Household care':
        if mass_merch_model.loc[i,'YEAR_int'] >= 2026:
            mass_merch_model.loc[i,'growth_share_annual'] = mass_merch_model.loc[i - 9,'CATEGORY_yoy_retailer']
            mass_merch_model.loc[i,'sales_added_share'] = ((mass_merch_model.loc[i - 9,'growth_multiplier']) / (mass_merch_model.loc[i,'growth_share_annual']))
            mass_merch_model.loc[i, 'cat_sales_diff'] = ((mass_merch_model.loc[i, 'CATEGORY_NETSALES']) - (mass_merch_model.loc[i - 9, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'subcategory_sales_diff'] = ((mass_merch_model.loc[i, 'cat_sales_diff']) * (mass_merch_model.loc[i, 'sales_added_share']))
            mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES'] = (
                        (mass_merch_model.loc[i - 9, 'SUBCATEGORY_NETSALES']) + (mass_merch_model.loc[i, 'subcategory_sales_diff']))
            mass_merch_model.loc[i, 'PCT_TOTAL'] = (
                        (mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'TOTAL_YOY'] = (
                ((mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i - 9, 'SUBCATEGORY_NETSALES'])) -1)
            mass_merch_model.loc[i, 'growth_multiplier'] = (
                    (mass_merch_model.loc[i - 9, 'PCT_TOTAL']) * (
                    mass_merch_model.loc[i, 'TOTAL_YOY']))
    elif mass_merch_model.loc[i, 'PRODUCTCATEGORY'] == 'Pet care':
        if mass_merch_model.loc[i,'YEAR_int'] >= 2026:
            mass_merch_model.loc[i,'growth_share_annual'] = mass_merch_model.loc[i - 6,'CATEGORY_yoy_retailer']
            mass_merch_model.loc[i,'sales_added_share'] = ((mass_merch_model.loc[i - 6,'growth_multiplier']) / (mass_merch_model.loc[i,'growth_share_annual']))
            mass_merch_model.loc[i, 'cat_sales_diff'] = ((mass_merch_model.loc[i, 'CATEGORY_NETSALES']) - (mass_merch_model.loc[i - 6, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'subcategory_sales_diff'] = ((mass_merch_model.loc[i, 'cat_sales_diff']) * (mass_merch_model.loc[i, 'sales_added_share']))
            mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES'] = (
                        (mass_merch_model.loc[i - 6, 'SUBCATEGORY_NETSALES']) + (mass_merch_model.loc[i, 'subcategory_sales_diff']))
            mass_merch_model.loc[i, 'PCT_TOTAL'] = (
                        (mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'TOTAL_YOY'] = (
                ((mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i - 6, 'SUBCATEGORY_NETSALES'])) -1)
            mass_merch_model.loc[i, 'growth_multiplier'] = (
                    (mass_merch_model.loc[i - 6, 'PCT_TOTAL']) * (
                    mass_merch_model.loc[i, 'TOTAL_YOY']))
    elif mass_merch_model.loc[i, 'PRODUCTCATEGORY'] == 'Health & Beauty':
        if mass_merch_model.loc[i,'YEAR_int'] >= 2026:
            mass_merch_model.loc[i,'growth_share_annual'] = mass_merch_model.loc[i - 11,'CATEGORY_yoy_retailer']
            mass_merch_model.loc[i,'sales_added_share'] = ((mass_merch_model.loc[i - 11,'growth_multiplier']) / (mass_merch_model.loc[i,'growth_share_annual']))
            mass_merch_model.loc[i, 'cat_sales_diff'] = ((mass_merch_model.loc[i, 'CATEGORY_NETSALES']) - (mass_merch_model.loc[i - 11, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'subcategory_sales_diff'] = ((mass_merch_model.loc[i, 'cat_sales_diff']) * (mass_merch_model.loc[i, 'sales_added_share']))
            mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES'] = (
                        (mass_merch_model.loc[i - 11, 'SUBCATEGORY_NETSALES']) + (mass_merch_model.loc[i, 'subcategory_sales_diff']))
            mass_merch_model.loc[i, 'PCT_TOTAL'] = (
                        (mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'TOTAL_YOY'] = (
                ((mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i - 11, 'SUBCATEGORY_NETSALES'])) -1)
            mass_merch_model.loc[i, 'growth_multiplier'] = (
                    (mass_merch_model.loc[i-11, 'PCT_TOTAL']) * (
                    mass_merch_model.loc[i, 'TOTAL_YOY']))
    elif mass_merch_model.loc[i, 'PRODUCTCATEGORY'] == 'Edible grocery':
        if mass_merch_model.loc[i,'YEAR_int'] >= 2026:
            mass_merch_model.loc[i,'growth_share_annual'] = mass_merch_model.loc[i - 13,'CATEGORY_yoy_retailer']
            mass_merch_model.loc[i,'sales_added_share'] = ((mass_merch_model.loc[i - 13,'growth_multiplier']) / (mass_merch_model.loc[i,'growth_share_annual']))
            mass_merch_model.loc[i, 'cat_sales_diff'] = ((mass_merch_model.loc[i, 'CATEGORY_NETSALES']) - (mass_merch_model.loc[i - 13, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'subcategory_sales_diff'] = ((mass_merch_model.loc[i, 'cat_sales_diff']) * (mass_merch_model.loc[i, 'sales_added_share']))
            mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES'] = (
                        (mass_merch_model.loc[i - 13, 'SUBCATEGORY_NETSALES']) + (mass_merch_model.loc[i, 'subcategory_sales_diff']))
            mass_merch_model.loc[i, 'PCT_TOTAL'] = (
                        (mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i, 'CATEGORY_NETSALES']))
            mass_merch_model.loc[i, 'TOTAL_YOY'] = (
                ((mass_merch_model.loc[i, 'SUBCATEGORY_NETSALES']) / (mass_merch_model.loc[i - 13, 'SUBCATEGORY_NETSALES'])) -1)
            mass_merch_model.loc[i, 'growth_multiplier'] = (
                    (mass_merch_model.loc[i - 13, 'PCT_TOTAL']) * (
                    mass_merch_model.loc[i, 'TOTAL_YOY']))
    else:
        pass

mass_merch_model = mass_merch_model[['MARKETNAME_x','RETAILERNAME','BANNERNAME','CHANNELNAME','FORMATNAME','YEAR_x','NETSALES','ly_netsales',
'NETSALES_yoy_retailer','PRODUCTCATEGORY','RI_SUBCATEGORY','YEAR_int','PCT_TOTAL',
        'TOTAL_YOY','PERCENTAGE_SPLIT','SUBCATEGORY_NETSALES','CATEGORY_NETSALES',
'growth_multiplier']]
for i in range(len(mass_merch_model)):
    if mass_merch_model.loc[i,'YEAR_int'] >= 2025:
        mass_merch_model['ly_subcategory_sales'] = mass_merch_model['SUBCATEGORY_NETSALES'].shift(11, fill_value = 0)
for i in range(len(mass_merch_model)):
    if mass_merch_model.loc[i,'BANNERNAME'] == 'Target.com':
        if mass_merch_model.loc[i,'PRODUCTCATEGORY'] == 'Edible grocery':
            mass_merch_model.loc[i,'CHANNELNAME'] = 'Supermarkets & Neighbourhood Stores'

mass_merch_model = mass_merch_model[mass_merch_model.YEAR_int <= 2031]
mass_merch_model = mass_merch_model[mass_merch_model.PERCENTAGE_SPLIT > 0]
mass_merch_model.columns = ['MARKETNAME','RETAILERNAME','BANNERNAME','CHANNELNAME','FORMATNAME','YEAR','NETSALES','ly_netsales',
'NETSALES_yoy_retailer','PRODUCTCATEGORY','PRODUCTSUBCATEGORY','YEAR_int','SUBCATEGORY_SPLIT',
        'total_yoy','PERCENTAGE_SPLIT','SUBCATEGORY_NETSALES','CATEGORY_NETSALES',
'growth_multiplier','ly_subcategory_sales']
mass_merch_model.sort_values(by = ['PRODUCTCATEGORY','BANNERNAME','FORMATNAME','PRODUCTSUBCATEGORY','YEAR_int'], inplace = True)
#mass_merch_model.reset_index(inplace = True)
mass_merch_model['YEAR'] = pd.to_datetime(mass_merch_model['YEAR'])
print(mass_merch_model['YEAR'].dtype == np.dtype('datetime64[ns]'))
session.write_pandas(
    df= mass_merch_model, 
    table_name = "PRODUCTION_TABLE", 
    database = "PRODUCTION_DB",
    schema = "PUBLIC",
    auto_create_table = True,
    overwrite = True,
    use_logical_type = True
)
