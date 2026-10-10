import pandas as pd
import numpy as np
import datetime as dt
import transform_data as td

market_cs = pd.read_csv('fw_cs_check_data.csv')
market_cs = pd.DataFrame(market_cs)
market_cs.drop(columns = ['api_flag'], inplace = True)
market_cs_max = market_cs.groupby(['RMM'])['Year'].max().reset_index()
market_cs_max.to_csv('max_years.csv')
gdp_lcu = pd.read_csv('2026_updated_gdp_report_lcu.csv')
market_cs = market_cs.pivot(index = ['RMM','MARKET','Year'],columns = 'Product_Category', values = 'PC_SPEND_LCU')
gdp_lcu.reset_index()
for i in range(len(gdp_lcu)):
    if gdp_lcu.loc[i,'NGDPD'] > 0:
        if gdp_lcu.loc[i,'YEAR'] >= 2011:
            gdp_lcu.loc[i,'cs_growth'] = np.log(gdp_lcu.loc[i,'NGDPD']) - np.log(gdp_lcu.loc[i-1,'NGDPD'])
market_spend = pd.merge(gdp_lcu, market_cs, how = 'left', left_on = ['RMM','YEAR'], right_on = ['RMM','Year']).reset_index()
market_spend = pd.merge(market_spend, market_cs_max, how = 'left', on = ['RMM']).reset_index()
for i in range(len(market_spend)):
    if pd.isna(market_spend.loc[i,'Year']):
        pass
    elif market_spend.loc[i,'YEAR'] >  market_spend.loc[i,'Year']:
        market_spend.loc[i,'Total_CS'] = market_spend.loc[i-1,'Total_CS'] * (1 + market_spend.loc[i,'cs_growth'])
market_spend.to_csv('THIS_IS_IT.csv')

gdp_lcu.to_csv('check_cs_calculation.csv')
#market_spend['cs_growth'] = np.log(market_spend['CS']) - np.log(market_spend['CS_Prev'])
market_spend = td.calc_prodcat(market_spend, 'Edible grocery', 0.010, 0.783, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Electricals', -0.027, 1.336, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Fashion & Apparel', -0.005, 1.029, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Foodservice', 0.017, 0.854, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Health & Beauty', 0.015, 0.837, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Home & DIY', -0.014, 1.212, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Household care', 0.004, 0.956, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Leisure & Entertainment', -0.020, 1.099, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Office', -0.007, 1.169, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Other retail products', -0.018, 1.351, 'cs_growth')
market_spend = td.calc_prodcat(market_spend, 'Pet care', 0.005, 1.172, 'cs_growth')
market_spend.to_csv('THIS_IS_IT_growth.csv')
