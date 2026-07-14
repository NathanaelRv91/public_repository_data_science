import pandas as pd
import numpy as np
from datetime import date
import os
import download_data as dd
import weight_cs as wc
import add_wb as aw
import forecast_cs as fc
#import calculate_rs as cr
import snowflake.connector
import add_imf as ai


coicop_lkp = pd.read_csv('coicop_lkp.csv')
oecd_lkp = dd.oecd_lkp()
market_map = dd.mrkt_lkp()
euro_gdp = pd.read_csv('euro_gdp_cleaned_oct_2025.csv')
euro_cs = pd.read_csv('euro_cs_cleaned_oct_2025.csv')
for i in range(len(euro_cs)):
    if euro_cs.loc[i,'Transaction'] == 'Personal effects n.e.c.':
        euro_cs.loc[i,'Transaction'] = 'Personal effects'
oecd_gdp = pd.read_csv('oecd_cs_gdp_oct_2025.csv')
oecd_cs = pd.read_csv('oecd_transaction_data_oct_2025.csv')
for i in range(len(oecd_cs)):
    if oecd_cs.loc[i,'Transaction'] == 'Personal effects n.e.c.':
        oecd_cs.loc[i,'Transaction'] = 'Personal effects'

wb_gdp = pd.read_csv('wb_cleaned_data_oct_2025.csv')
oecd_gdp = dd.market_uniform(oecd_gdp, market_map)
euro_gdp = dd.market_uniform(euro_gdp, market_map)
wb_gdp = dd.market_uniform(wb_gdp, market_map)
oecd_cs = dd.market_uniform(oecd_cs, market_map)
euro_cs = dd.market_uniform(euro_cs, market_map)
gdp_mstr = dd.master_merge([oecd_gdp, euro_gdp, wb_gdp], ['RMM', 'Year'])
cs_mstr = dd.master_merge([oecd_cs, euro_cs], ['RMM', 'Year', 'Transaction'])
mrkt_class = dd.mrkt_class()
gdp_mstr = dd.cross_join(gdp_mstr, mrkt_class)
cs_mstr = dd.cs_cross_join(cs_mstr, mrkt_class)
gdp_mstr = dd.pick_value(gdp_mstr, 'GDP')
gdp_mstr = dd.pick_value(gdp_mstr, 'CS')
gdp_mstr = dd.calc_avg(gdp_mstr)
cs_gdp = dd.cs_oecd_euro(cs_mstr, gdp_mstr, mrkt_class)
cs_gdp = dd.act_est(cs_gdp)
hier_weight, map_weight, coicop, hier = wc.cs_input()
cs_gdp1 = wc.cs_wrangle(cs_gdp, hier_weight)
cs_gdp2 = wc.level_weights(cs_gdp1, coicop, map_weight)
cs_gdp3 = wc.calc_levels(cs_gdp2, mrkt_class)

c2 = wc.determine_level_calc(cs_gdp3, 'c2', '2', '1')
c3 = wc.determine_level_calc(cs_gdp3, 'c3', '3', '2')
c4 = wc.determine_level_calc(cs_gdp3, 'c4', '4', '3')
c_master = c2._append([c3, c4])
cs_gdp3 = wc.category_name(cs_gdp3)
cs_gdp3 = wc.identify_missing_yrs(cs_gdp3)
cs_gdp4 = cs_gdp3.copy()
cs_gdp4 = wc.identify_calcs(cs_gdp4, 2, '1', c_master)
cs_gdp4 = wc.identify_calcs(cs_gdp4, 3, '2', c_master)
cs_gdp4 = wc.identify_calcs(cs_gdp4, 4, '3', c_master)
cs_gdp4 = wc.coalsece_val(cs_gdp4)
cat_df1 = wc.cat1(cs_gdp4)
cat_df2 = wc.cat1_qa(cat_df1)
cs_gdp5 = wc.cat2(cat_df2, cs_gdp4)
cs_gdp6 = wc.l2_rebase_calc(cs_gdp5)


cs_gdp7 = wc.l3_l4_rebase(cs_gdp6)
cs_gdp8 = cs_gdp7[['RMM', 'Transaction', 'Year', 'ActEst', 'Method', 'Forecast', 'MARKET_CLASS', 'MARKET_CLASS_v2',
                   'Category1', 'Category2', 'Category3', 'Category4', 'level', 'cs_pct_c1', 'cs_pct_c2',
                   'cs_pct_c3', 'cs_pct_c4', 'value']]

cs_act = cs_gdp[['RMM', 'Transaction', 'Year', 'value']]
df = pd.merge(left=cs_gdp8, right=cs_act, how='left', on=['RMM', 'Transaction', 'Year'])
cs_gdp9, rename = wc.name_input(cs_gdp8)
cs_gdp9 = wc.category_name(cs_gdp9)

gdp_mstr = gdp_mstr[['RMM', 'Year', 'GDP_mstr', 'CS_mstr', 'cs_pct_mstr']]
cs_gdp9 = pd.merge(left=cs_gdp9, right=gdp_mstr, how='left', on=['Year', 'RMM'], suffixes=('', '_DROP')).filter(
    regex='^(?!.*_DROP)')
cols = ['cs_pct_c1', 'cs_pct_c2', 'cs_pct_c3', 'cs_pct_c4']
cs_gdp9[cols] = cs_gdp9[cols].apply(pd.to_numeric, errors='coerce')
cs_gdp9['val_flag'] = np.where(cs_gdp9['cs_pct_c1'] > 0, 1, 0)
cs_gdp9['cs_abs_c1'] = cs_gdp9['CS_mstr']*cs_gdp9['cs_pct_c1']
cs_gdp9['cs_abs_c2'] = cs_gdp9['CS_mstr']*cs_gdp9['cs_pct_c2']
cs_gdp9['cs_abs_c3'] = cs_gdp9['CS_mstr']*cs_gdp9['cs_pct_c3']
cs_gdp9['cs_abs_c4'] = cs_gdp9['CS_mstr']*cs_gdp9['cs_pct_c4']
cs_gdp9.to_csv('TEST_cs_gdp9.csv')
# add_wb.py
wb_icp = pd.read_excel('Data_Extract_From_ICP_2021.xlsx', sheet_name='Data')
wb_pc = aw.clean_wb_icp(wb_icp)
wb_pc.to_csv('TEST_wb_clean.csv')
for i in range(len(wb_pc)):
    if wb_pc.loc[i,'Market'] == 'Congo, Rep.':
        wb_pc.loc[i,'Market'] = 'Congo Republic'
    if wb_pc.loc[i,'Market'] == 'Congo, Dem. Rep.':
        wb_pc.loc[i,'Market'] = 'Congo Democratic Republic'
    else:
        pass
market_map = dd.mrkt_lkp()
wb_pc1 = aw.mrkt_map(wb_pc, market_map)
wb_pc1.to_csv('TEST_wb_map.csv')
wb_base_cs = aw.cs_merge(wb_pc1, mrkt_class)
wb_base_cs.to_csv('TEST_wb_cs_merge.csv')
for i in range(len(wb_base_cs)):
    if wb_base_cs.loc[i,'Market'] == 'Congo, Republic':
        wb_base_cs.loc[i,'Market'] = 'Congo Republic'
    if wb_base_cs.loc[i,'Market'] == 'Congo, Democratic Republic':
        wb_base_cs.loc[i,'Market'] = 'Congo Democratic Republic'
    else:
        pass
wb_base_mapped = aw.missing_calcs(wb_base_cs)
wb_base_mapped.to_csv('TEST_wb_calc_missing.csv')
wb_base_mapped = \
    wb_base_mapped[['Year', 'RMM', 'MARKET_CLASS', 'Category1', 'ActEst', 'Method', 'pct', 'Value_x']]

wb_2006 = aw.constant_interp(wb_base_mapped, 2009, 2016, 2017)
wb_2006 = aw.interp_between(wb_2006, 2009, 2016)
wb_2018 = aw.constant_interp(wb_base_mapped, 2022, 2023,2021)
wb_missing = aw.interp_between(wb_base_mapped, 2017, 2021)
wb_missing.to_csv('TEST_interp_between.csv')
wb_base = aw.intrp_act_merge(wb_2006, wb_2018, wb_missing)
wb_base.to_csv('TEST_interp_merge.csv')
wb_base = aw.mrkt_bmrk(wb_base, wb_base)
wb_base.to_csv('TEST_mrkt_bmrk.csv')

wb_base1, cs_gdp = aw.cs_cleanup(wb_base, gdp_mstr, cs_gdp9, mrkt_class)
wb_base1.to_csv('TEST_wb_cleanup_gdp.csv')
df = aw.cross_join(wb_base1, hier_weight)
df.to_csv('TEST_wb_cross_join.csv')
df1 = aw.calc_levels(df, coicop, map_weight)
df1.to_csv('TEST_wb_calc_levels.csv')
df1 = aw.name_input(df1)
df1.to_csv('TEST_wb_name_input.csv')
df1 = aw.category_name(df1)
df1.to_csv('TEST_wb_category_name.csv')
df1['Source'] = 'WB ICP'

df2, gdp_mstr, unq_mrkt, src_check = aw.append_src(df1, gdp_mstr, cs_gdp, mrkt_class, cs_gdp9)
df2.to_csv('TEST_bring_EUROOECD.csv')

classification = dd.mrkt_class()
cs_bmrk = gdp_mstr[gdp_mstr.cs_pct_mstr != 0]
cs_bmrk = cs_bmrk.dropna(subset=['cs_pct_mstr'])
cs_bmrk = pd.merge(cs_bmrk, classification, how='left', on='RMM')
cs_bmrk = cs_bmrk.groupby(['Year', 'MARKET_CLASS_v2']).agg(avg_cs_pct=('cs_pct_mstr', 'mean')).reset_index()

df3 = pd.merge(df2, cs_bmrk, how='left', on=['Year', 'MARKET_CLASS_v2'])
df3['GDP_mstr'].replace({np.nan: 0}, inplace=True)
df3['CS_mstr'].replace({np.nan: 0}, inplace=True)

#df3.to_csv('world_bank_check_new_data.csv')
for i in range(len(df3)):
    if df3.loc[i, 'Method'] == 'C':
        df3.loc[i, 'CS_mstr'] = df3.loc[i, 'avg_cs_pct'] * df3.loc[i, 'GDP_mstr']
    else:
        pass

df3 = df3[df3['Year'] < 2024].reset_index(drop=True)
df3.to_csv('retail_cs_model.csv')

map_pc2 = pd.read_csv('2025_PC_Map_Main.csv')

df3 = df3[['Year', 'RMM', 'MARKET_CLASS', 'MARKET_CLASS_v2', 'Source', 'Category1Code', 'Category2Code',
           'Category3Code', 'Category4Code', 'cs_abs_c1', 'cs_abs_c2', 'cs_abs_c3', 'cs_abs_c4']]

melt1 = pd.melt(df3, id_vars=['Year', 'RMM', 'Category1Code', 'MARKET_CLASS', 'MARKET_CLASS_v2', 'Source'])
melt1 = melt1[(melt1.variable == 'cs_abs_c1') & (melt1.value != 0.0)]
melt1.rename(columns={'Category1Code': 'CodeCategory'}, inplace=True)

melt2 = pd.melt(df3, id_vars=['Year', 'RMM', 'Category2Code', 'MARKET_CLASS', 'MARKET_CLASS_v2', 'Source'])
melt2 = melt2[(melt2.variable == 'cs_abs_c2') & (melt2.value != 0.0)]
melt2.rename(columns={'Category2Code': 'CodeCategory'}, inplace=True)

melt3 = pd.melt(df3, id_vars=['Year', 'RMM', 'Category3Code', 'MARKET_CLASS', 'MARKET_CLASS_v2', 'Source'])
melt3 = melt3[(melt3.variable == 'cs_abs_c3') & (melt3.value != 0.0)]
melt3.rename(columns={'Category3Code': 'CodeCategory'}, inplace=True)


melt4 = pd.melt(df3, id_vars=['Year', 'RMM', 'Category4Code', 'MARKET_CLASS', 'MARKET_CLASS_v2', 'Source'])
melt4 = melt4[(melt4.variable == 'cs_abs_c4') & (melt4.value != 0.0)]
melt4.rename(columns={'Category4Code': 'CodeCategory'}, inplace=True)

melt_mstr = melt1._append([melt2, melt3, melt4])

melt_mstr['CodeCategory'] = melt_mstr['CodeCategory'].str.strip()

map_melt = pd.merge(melt_mstr, map_pc2, how='inner', on='CodeCategory')
pc_agg = map_melt.groupby(['Year', 'RMM', 'Product Category', 'MARKET_CLASS', 'MARKET_CLASS_v2', 'Source'],
                          dropna=True).agg(PC_Tot=('value', 'sum')).reset_index()

pc_tot = pc_agg.groupby(['Year', 'RMM'], dropna=True).agg(Tot=('PC_Tot', 'sum')).reset_index()
pc_agg = pd.merge(pc_agg, pc_tot, how='left', on=['Year', 'RMM'])
pc_agg= pc_agg[pc_agg.Tot !=0]
pc_agg['pc_share'] = pc_agg['PC_Tot'] / pc_agg['Tot']
pc_agg = pd.merge(pc_agg, gdp_mstr, how='left', on=['Year', 'RMM'])
df = pc_agg
pc_agg.to_csv('TEST_category_reshape.csv')

# allows us to start forecasting the year after the last year of historical data (not the same for all markets)
df_id = df[['Year', 'RMM', 'Tot', 'GDP_mstr']].drop_duplicates()
df_id = df_id[df_id.Tot != 0.0]
df_id.rename(columns={'Tot': 'CS_Avail'}, inplace=True)
# total consumer spending share of GDP
df_id['cs_pct'] = df_id['CS_Avail'] / df_id['GDP_mstr']

df_max = df_id.groupby(['RMM']).agg(max_year=('Year', 'max')).reset_index()
cs_rmm = pd.merge(df_id, df_max, how='inner', left_on=['RMM', 'Year'], right_on=['RMM', 'max_year'])
cs_rmm = cs_rmm[['RMM', 'cs_pct', 'CS_Avail', 'max_year']]
df = pd.merge(df, df_id, how='left', on=['Year', 'RMM'], suffixes=('', '_DROP')).filter(regex='^(?!.*_DROP)')
df['CS_Avail'].replace({np.nan: 0}, inplace=True)
df['Forecast'] = np.where(df['CS_Avail'] == 0, 'F', '')

gdp = ai.pull_imf()
gdp= ai.conv_gdp(gdp)

forex = pd.read_csv('2025_exchange_rates.csv')
df = df.merge(forex, how='left', right_on=['Country', 'Year'], left_on=['RMM', 'Year'])
df.drop('Country', axis=1, inplace=True)
#df.drop('Year', axis=1, inplace=True)
df.drop('IMF_rate', axis=1, inplace=True)
df.drop('ERI_rate', axis=1, inplace=True)
gdp1 = pd.merge(gdp, cs_rmm, how='left', on='RMM')

gdp1 = gdp1[['RMM', 'YEAR', 'NGDPD', 'cs_pct', 'CS_Avail', 'max_year']]
gdp1 = gdp1.sort_values(by=['RMM', 'YEAR']).reset_index(drop=True)
gdp1['GDP_Prev'] = gdp1.sort_values(by=['YEAR', 'RMM'], ascending=True).groupby(['RMM'])['NGDPD'].shift(1)
gdp1.to_csv('test_gdp1.csv')
gdp1['YoY_Chg_LN'] = np.log(gdp1['NGDPD']) - np.log(gdp1['GDP_Prev'])
gdp1['cs_growth']= (gdp1['YoY_Chg_LN'] * 0.504) + ( gdp1['YoY_Chg_LN'] * 0.823) * gdp1['cs_pct']
gdp2 = gdp1[['RMM', 'YEAR', 'cs_growth', 'CS_Avail', 'max_year']]
gdp3 = pd.merge(gdp2, df_id, how='left', left_on=['YEAR', 'RMM'], right_on=['Year', 'RMM'])
gdp3['id_fcast'] = np.where(gdp3['YEAR'] >= gdp3['max_year'], 1, 0)
gdp3 = gdp3[gdp3.id_fcast == 1]  # these are the years we need to forecast
gdp3['idx'] = gdp3.groupby(['RMM']).cumcount()
gdp3['CS'] = 0
gdp3 = gdp3.reset_index()
gdp3.drop(['index'], axis=1, inplace=True)


# if we don't have data, approximate CS by applying the estimated CS growth rate to CS from the previous year
for i in range(len(gdp3)):
    if gdp3['idx'][i] == 0.0:
        gdp3['CS'][i] = gdp3['CS_Avail_y'][i]
    else:
        # generate forecast for the absolute values of consumer spending with our forecasted growth rate from above
        gdp3['CS'][i] = (gdp3['CS'][i - 1]) * (1 + gdp3['cs_growth'][i])

# create a row with the CS data from the previous year by market and year
gdp3['CS_Prev'] = gdp3.sort_values(by=['Year', 'RMM'], ascending=True).groupby(['RMM'])['CS'].shift(1)

# calculate the year-on-year growth of CS (use natural log)
gdp3['YoY_CS_LN'] = np.log(gdp3['CS']) - np.log(gdp3['CS_Prev'])
gdp3.to_csv('TEST_fcast_vars.csv')
gdp3 = fc.calc_prodcat(gdp3, 'Edible grocery', 0.010, 0.783, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Electricals', -0.027, 1.336, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Fashion & Apparel', -0.005, 1.029, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Foodservice', 0.017, 0.854, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Health & Beauty', 0.015, 0.837, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Home & DIY', -0.014, 1.212, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Household care', 0.004, 0.956, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Leisure & Entertainment', -0.020, 1.099, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Office', -0.007, 1.169, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Other retail products', -0.018, 1.351, 'YoY_CS_LN')
gdp3 = fc.calc_prodcat(gdp3, 'Pet care', 0.005, 1.172, 'YoY_CS_LN')

df_pc = pd.merge(df, cs_rmm, how='inner', left_on=['Year', 'RMM'], right_on=['max_year', 'RMM'])
df_pc = df_pc[['Year', 'RMM', 'Product Category', 'PC_Tot']]
df_pc = df_pc[df_pc['PC_Tot'] != 0]
# pivot the prod cat column so the prod cats are individual columns
df_pc1 = df_pc.pivot(index=['Year', 'RMM'], columns='Product Category')['PC_Tot'].reset_index()
# join the pivoted historical prod cat values with our estimated prod cat growth rates
gdp4 = pd.merge(gdp3, df_pc1, how='left', left_on=['YEAR', 'RMM'], right_on=['Year', 'RMM'])
gdp4 = fc.pc_pop('Edible grocery', gdp4)
gdp4 = fc.pc_pop('Electricals', gdp4)
gdp4 = fc.pc_pop('Fashion & Apparel', gdp4)
gdp4 = fc.pc_pop('Foodservice', gdp4)
gdp4 = fc.pc_pop('Health & Beauty', gdp4)
gdp4 = fc.pc_pop('Home & DIY', gdp4)
gdp4 = fc.pc_pop('Household care', gdp4)
gdp4 = fc.pc_pop('Leisure & Entertainment', gdp4)
gdp4 = fc.pc_pop('Office', gdp4)
gdp4 = fc.pc_pop('Other retail products', gdp4)
gdp4 = fc.pc_pop('Pet care', gdp4)

gdp5 = gdp4.copy()
gdp5.to_csv('TEST_gdp_retail_model.csv')

pc_list = ['RMM', 'YEAR', 'cs_pct', 'cs_growth', 'CS', 'GDP_mstr', 'Edible grocery', 'Electricals',
           'Fashion & Apparel', 'Foodservice', 'Health & Beauty', 'Home & DIY', 'Household care',
           'Leisure & Entertainment', 'Office', 'Other retail products', 'Pet care']
gdp4 = gdp4[pc_list]

gdp4['PC TOT Sum'] = gdp4.iloc[:, 6:].sum(axis=1)
pc_melt = pd.melt(gdp4, id_vars=['RMM', 'YEAR', 'cs_pct', 'cs_growth', 'CS', 'GDP_mstr', 'PC TOT Sum'],
                      value_name='PC FCAST', var_name='Product Category')
# check to ensure we have no 0 forecasted values
print(sum(pc_melt['PC FCAST'] == 0))
dist_df = df[['RMM', 'Product Category']].drop_duplicates()
yr_df = pd.DataFrame(data=range(2009, 2031), columns=['YEAR'])
df_mstr = dist_df.merge(yr_df, how='cross')
pc_output = df_mstr.merge(pc_melt, how='left', on=['YEAR', 'RMM', 'Product Category'])

pc_output = pd.merge(pc_output, df, how='left', left_on=['YEAR', 'RMM', 'Product Category'],
                        right_on=['Year', 'RMM', 'Product Category'],
                        suffixes=('', '_DROP')).filter(regex='^(?!.*_DROP)')
pc_output.drop('Year', axis=1, inplace=True)

pc_output['PC_Tot'].replace({np.nan: 0}, inplace=True)
pc_output['Forecast'] = np.where(pc_output['PC_Tot'] == 0, 'F', 'A')
pc_output['PC_Tot'] = np.where(pc_output['Forecast'] == 'F', pc_output['PC FCAST'], pc_output['PC_Tot'])
pc_output['Tot'] = np.where(pc_output['Forecast'] == 'F', pc_output['PC TOT Sum'], pc_output['Tot'])
# join in the GDP data
gdp = gdp1[['YEAR', 'RMM', 'NGDPD']]
pc_output = pd.merge(pc_output, gdp, how='left', on=['YEAR', 'RMM'])
pc_output = pc_output.loc[:, ['RMM', 'Product Category', 'YEAR', 'PC_Tot', 'Tot', 'Forecast']]
pc_output.to_csv('cs_model_check1.csv')
pc_pivot = pd.pivot_table(pc_output, values=['PC_Tot'], index=['RMM', 'YEAR', 'Tot', 'Forecast'],
                            columns=['Product Category']).swaplevel(0, 1, axis=1).reset_index()

pc_pivot.columns = pc_pivot.columns.map('_'.join)
pc_pivot.rename(columns={'RMM_': 'RMM', 'YEAR_': 'YEAR', 'Tot_': 'CONSUMER_SPENDING', 'Forecast_': 'Forecast',
                            'Edible grocery_PC_Tot': 'EDIBLE_GROCERY', 'Electricals_PC_Tot': 'CONSUMER_ELECTRONICS',
                            'Fashion & Apparel_PC_Tot': 'CLOTHING_FOOTWEAR_ACCESSORIES',
                            'Foodservice_PC_Tot': 'FOODSERVICE', 'Health & Beauty_PC_Tot': 'HEALTH_BEAUTY',
                            'Home & DIY_PC_Tot': 'DIY_FURNITURE_HOMEWARES', 'Household care_PC_Tot': 'HOUSEHOLD',
                            'Leisure & Entertainment_PC_Tot': 'ENTERTAINMENT',
                            'Office_PC_Tot': 'OFFICE_SUPPLIES', 'Other retail products_PC_Tot': 'AUTOMOTIVE_PRODUCTS',
                            'Pet care_PC_Tot': 'PET_CARE'}, inplace=True)
pc_pivot.to_snowflake('TEST_master_check_consumer_spending')
pc_pivot = pd.DataFrame(pc_pivot)
pc_pivot = pc_pivot.drop_duplicates(subset = ['RMM','YEAR'], keep = 'first', inplace = True)


conn = snowflake.connector.connect(
    user="NATHANAEL_RICHARDSON",
    password="MY_PASSWORD",
    account="MY_ACCOUNT_IDENTIFIER",
    warehouse="WH_PRODUCTION_SMALL",
    database="PRODUCTION_DATABASE",
    schema="PUBLIC"
)

try:
    # 3. Write DataFrame to Snowflake
    # Set auto_create_table=True if the table does not exist yet
    success, nchunks, nrows, _ = write_pandas(
        conn=conn, 
        df=pc_pivot, 
        table_name="CONSUMER_SPENDING_MODEL", 
        auto_create_table=True,
        overwrite=False
    )
    print(f"Successfully uploaded {nrows} rows.")
    
finally:
    conn.close()
