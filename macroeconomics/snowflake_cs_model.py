import pandas as pd
import numpy as np
import transform_data as td
#import build_world_bank_cs as wb
import consumer_spending_build as cs
import datetime as dt
import math
#import add_imf as ai

classifications = pd.read_excel('Market_Classifications_2026.xlsx', sheet_name='Market Classification')
map = pd.read_csv('2026_market_map.csv')
market_rates = pd.read_csv('model_rates.csv')
euro_cs = pd.read_csv('euro_cs_coicop_cleaned.csv')
euro_gdp = pd.read_csv('euro_cs_gdp_cleaned.csv')
coicop_bmrk = pd.read_csv('coicop_bmrk.csv')
oecd_cs = pd.read_csv('final_api_df_COICOP_NEW_group3.csv')
oecd_gdp = pd.read_csv('oecd_cs_gdp_cleaned_oct.csv')
oecd_cs_2018 = pd.read_csv('oecd_cs_coicop2018_cleaned_oct.csv')
weights = pd.read_csv('map_weight.csv')
hier = pd.read_csv('hier_weight.csv')
pc_fw_map = pd.read_csv('pc_map_coicop_fw.csv')

euro_full_report = cs.build_eurostat_cs(euro_cs,euro_gdp,map,market_rates,classifications, coicop_bmrk)
#oecd_non_euro_report = cs.build_oecd_cs_1999(oecd_cs,oecd_gdp,map,classifications,market_rates,coicop_bmrk)
oecd_euro_report = cs.build_oecd_cs_2018(oecd_cs_2018,oecd_gdp,map,classifications,market_rates)
oecd_non_euro_report = cs.build_oecd_cs_2018(oecd_cs,oecd_gdp,map,classifications,market_rates)

oecd_all = pd.concat([oecd_euro_report,oecd_non_euro_report],axis = 0)
oecd_all.reset_index(inplace = True)
cs_all = pd.concat([oecd_all,euro_full_report], axis = 0)
cs_wb_l2 = cs_all.copy()
oecd_rmms = pd.DataFrame(oecd_all['RMM'].drop_duplicates())
oecd_rmms.columns = ['oecd_available']
eurostat_rmms = pd.DataFrame(euro_full_report['RMM'].drop_duplicates())
eurostat_rmms.columns = ['euro_available']
api_rmms = pd.merge(oecd_rmms,eurostat_rmms, how = 'outer', left_on = 'oecd_available', right_on = 'euro_available')
api_rmms.reset_index(inplace = True)

for i in range(len(api_rmms)):
    if pd.isna(api_rmms.loc[i,'oecd_available']):
        api_rmms.loc[i,'use_flag'] = 1
    else:
        api_rmms.loc[i,'use_flag'] = 0

api_rmms = api_rmms[api_rmms.use_flag == 1]
eurostat_data = pd.merge(euro_full_report,api_rmms, how = 'inner', left_on = 'RMM', right_on = 'euro_available').reset_index()
eurostat_data.drop(columns = ['index','oecd_available','euro_available','use_flag','level_0'], inplace = True)
eurostat_data['api_flag'] = 'EUROSTAT'
oecd_all['api_flag']= 'OECD'
cs_all = pd.concat([oecd_all,eurostat_data], axis = 0)
cs_all = cs_all[['RMM','Market','Year','COICOP','Transaction','CS_EURO','CS_USD','flag','IMF_rate','MARKET_CLASS','MARKET_CLASS_v2','GDP_EURO','CS_pct_EURO','GDP_USD','LEVEL','CS_USD_REBASE_L2','CS_L1_USD','api_flag']]
cs_all.reset_index(inplace = True)

for i in range(len(cs_all)):
    if cs_all.loc[i,'Transaction'] == 'Personal effects n.e.c.':
        cs_all.loc[i, 'Transaction'] = 'Personal effects'
cs_all = cs_all[['RMM','Market','Year','COICOP','Transaction','CS_EURO','CS_USD','flag','IMF_rate','MARKET_CLASS','MARKET_CLASS_v2','GDP_EURO','CS_pct_EURO','GDP_USD','LEVEL','CS_USD_REBASE_L2','CS_L1_USD','api_flag']]

pc_fw_map['Product_Category'] = pc_fw_map['Product_Category'].astype(str)
cs_all = pd.DataFrame(cs_all[(cs_all.api_flag.isin(['EUROSTAT'])) & (cs_all.Year >= 2010)])

cs_hier = pd.merge(cs_all,hier, how = 'left', left_on = ['MARKET_CLASS','Transaction'], right_on = ['MarketClass','Category2'])
cs_hier.reset_index()

cs_hier = pd.merge(cs_hier,weights, how = 'left', left_on = ['MarketClass','Category3'], right_on = ['MarketClass','Code'])
cs_hier.rename(columns = {'Weight_y':'Weight_3','Weight_x':'Weight_Base'}, inplace = True)
cs_hier.drop(columns = ['Desc','Remove'],inplace = True)
cs_hier = pd.merge(cs_hier,weights, how = 'left', left_on = ['MarketClass','Category4'], right_on = ['MarketClass','Code'])
cs_hier.drop(columns = ['Desc','Remove','Series_y','Weight_Base'],inplace = True)
cs_hier.rename(columns = {'Weight':'Weight_4', 'Code_x':'Code_3','Code_y':'Code_4','Product Category_x':'Product_Category_3','Product Category_y':'Product_Category_4'}, inplace = True)
for i in range(len(cs_hier)):
    if str(cs_hier.loc[i,'Code_3']) in (['11.03.11.0','11.03.12.0','11.03.14.0','11.03.21.0','11.03.22.0','11.04.31.0','11.04.32.0','11.05.11.0','11.05.12.0','11.05.13.0','11.05.31.0','11.05.32.0','11.05.33.0','11.05.61.0','11.05.62.0','11.09.11.0','11.09.14.0','11.09.15.0','11.09.21.0','11.09.23.0','11.09.31.0','11.09.33.0','11.09.35.0','11.12.11.0','11.12.12.0','11.12.31.0','11.12.32.0']):
        cs_hier.loc[i,'LEVEL'] = 3
        if str(cs_hier.loc[i,'Code_4']) in (['EU A.09.11.1','EU A.09.11.2','EU A.09.11.3','EU A.09.11.9','EU A.09.12.0','EU A.09.13.1','EU A.09.13.2','EU A.09.13.3','EU A.09.13.4','EU A.09.21.0','EU A.09.22.0','EU A.09.33.1','EU A.09.33.2','EU A.09.34.0']):
            cs_hier.loc[i, 'LEVEL'] = 4

for i in range(len(cs_hier)):
    if cs_hier.loc[i,'LEVEL'] == 3:
        cs_hier.loc[i, 'PC_CS_L3'] = cs_hier.loc[i, 'CS_USD'] * cs_hier.loc[i, 'Weight_3']

for i in range(len(cs_hier)):
    if cs_hier.loc[i,'LEVEL'] == 4:
        cs_hier.loc[i, 'PC_CS_L4'] = cs_hier.loc[i, 'CS_USD'] * cs_hier.loc[i, 'Weight_3'] * cs_hier.loc[i,'Weight_4']
#######################################################
### Level 1 & Level 2 Rename for Mapping ##
#######################################################
for i in range(len(cs_hier)):
    if cs_hier.loc[i,'LEVEL'] == 1:
        cs_hier.loc[i,'Code_Main'] = cs_hier.loc[i,'COICOP']
        cs_hier.loc[i,'PC_CS_L1'] = cs_hier.loc[i,'CS_USD']
    elif cs_hier.loc[i,'LEVEL'] == 2:
        cs_hier.loc[i,'Code_2'] = cs_hier.loc[i,'COICOP']
        cs_hier.loc[i, 'PC_CS_L2'] = cs_hier.loc[i, 'CS_USD']

cs_levels = pd.merge(cs_hier,pc_fw_map, how = 'left', left_on = 'COICOP', right_on = 'CodeCategory')
cs_levels.reset_index(inplace = True)
for i in range(len(cs_levels)):
    if cs_levels.loc[i,'LEVEL'] == 1:
        cs_levels.loc[i,'Product_Category_1'] = str(cs_levels.loc[i,'Product_Category'])
    elif cs_levels.loc[i,'LEVEL'] == 2:
        cs_levels.loc[i,'Product_Category_2'] = str(cs_levels.loc[i, 'Product_Category'])

cs_levels['Product_Category_1'] = cs_levels['Product_Category_1'].replace({'nan': None})
cs_levels['Product_Category_2'] = cs_levels['Product_Category_2'].replace({'nan': None})

#cs_columns --> [['RMM','Market','Year','COICOP','Transaction','CS_EURO','CS_USD','IMF_rate','MARKET_CLASS','MARKET_CLASS_v2','GDP_EURO','GDP_USD','LEVEL','api_flag','Code_1','Product_Category','Code_3','Weight_3','Product_Category_3','Code_4','Weight_4','Product_Category_4','PC_CS_L3','PC_CS_L4','Code_2','PC_CS_L2','Code_Main','PC_CS_L1']]
cs_l1 = cs_levels[cs_levels.LEVEL == 1]
cs_l1 = pd.DataFrame(cs_l1[['RMM','Market','Year','COICOP','Transaction','PC_CS_L1','Product_Category_1','IMF_rate','api_flag']])
cs_l1.columns = ['RMM','Market','Year','COICOP','Transaction','PC_CS','Product_Category','IMF_rate','api_flag']

cs_l2 = cs_levels[cs_levels.LEVEL == 2]
cs_l2 = pd.DataFrame(cs_l2[['RMM','Market','Year','COICOP','Transaction','PC_CS_L2','Product_Category_2','IMF_rate','api_flag']])
cs_l2.columns = ['RMM','Market','Year','COICOP','Transaction','PC_CS','Product_Category','IMF_rate','api_flag']

cs_l3 = cs_levels[cs_levels.LEVEL == 3]
cs_l3 = pd.DataFrame(cs_l3[['RMM','Market','Year','COICOP','Transaction','PC_CS_L3','Product_Category_3','IMF_rate','api_flag']])
cs_l3.columns = ['RMM','Market','Year','COICOP','Transaction','PC_CS','Product_Category','IMF_rate','api_flag']

cs_l4 = cs_levels[cs_levels.LEVEL == 4]
cs_l4 = pd.DataFrame(cs_l4[['RMM','Market','Year','COICOP','Transaction','PC_CS_L4','Product_Category_4','IMF_rate','api_flag']])
cs_l4.columns = ['RMM','Market','Year','COICOP','Transaction','PC_CS','Product_Category','IMF_rate','api_flag']

cs_mapped = pd.concat([cs_l1,cs_l2,cs_l3,cs_l4], axis = 0)

cs_mapped = cs_mapped.groupby(['RMM','Market','Year','Product_Category']).agg(
    imf_rate = ('IMF_rate','min'),
    pc_spend = ('PC_CS','sum')
).reset_index()

cs_mapped_total = cs_mapped.groupby(['RMM','Market','Year']).agg(
imf_rate = ('imf_rate','min'),
    pc_spend = ('pc_spend','sum')

).reset_index()
cs_mapped_total['Product_Category'] = 'Total_CS'
cs_mapped_total['PC_SPEND_LCU'] = cs_mapped_total['pc_spend'] * cs_mapped_total['imf_rate']
cs_mapped_total = cs_mapped_total[['RMM','Market','Year','Product_Category','imf_rate','pc_spend','PC_SPEND_LCU']]
cs_mapped['PC_SPEND_LCU'] = cs_mapped['pc_spend'] * cs_mapped['imf_rate']
cs_oecdeuro = pd.concat([cs_mapped,cs_mapped_total],axis = 0)
cs_oecdeuro.sort_values(by = ['Year','Market','Product_Category'], inplace = True)
oecd_data = cs_oecdeuro.copy()
##################################################################
################## BUILD World Bank CS MODEL #####################
##################################################################
wb_cs = pd.read_csv('wb_cs_gdp_cleaned_oct.csv')
hierarchy_wb_cs = pd.read_csv('wb_cs_hierarchy_v2.csv')
wb_icp = pd.read_excel('wb_icp_data_extract.xlsx', sheet_name='Data')
wb_pc = td.clean_wb_icp(wb_icp)
for i in range(len(wb_pc)):
    if wb_pc.loc[i,'Market'] == 'Congo, Rep.':
        wb_pc.loc[i,'Market'] = 'Congo Republic'
    if wb_pc.loc[i,'Market'] == 'Congo, Dem. Rep.':
        wb_pc.loc[i,'Market'] = 'Congo Democratic Republic'
    else:
        pass
wb_pc1 = td.mrkt_map(wb_pc, map)
src = wb_pc1
cs = src[src['Series'] == '9100000:HOUSEHOLDS AND NPISHS FINAL CONSUMPTION EXPENDITURE']
cs = cs[['Market', 'Year', 'Value']].drop_duplicates()
cs.reset_index(inplace = True)
wb_base_cs = pd.merge(left=src, right=cs, how='left', left_on=['Year', 'Market'], right_on=['Year', 'Market'])
wb_base_cs = pd.DataFrame(wb_base_cs)
wb_base_cs['Value_x'] = wb_base_cs['Value_x'].astype(float)
wb_base_cs['pct'] = wb_base_cs['Value_x'] / wb_base_cs['Value_y']
wb_base_cs.sort_values(by=['Market', 'Year'], ascending=[True, True], inplace=True)
# join in the market class table to bring the different market classifications
wb_base_cs = pd.merge(left=wb_base_cs, right=classifications, how='left', left_on=['Market'], right_on=['RMM'],
                        suffixes=('', '_DROP')).filter(regex='^(?!.*_DROP)')

wb_base_cs['ActEst'] = np.where(wb_base_cs['Value_x'] > 0, 'A', 'E')
wb_base_mapped = td.missing_calcs(wb_base_cs)
wb_base_mapped = wb_base_mapped[['Year', 'RMM', 'MARKET_CLASS', 'Category1', 'ActEst', 'Method', 'pct', 'Value_x']]
## You will need to update these values and understand the add_wb functions so once the 2025 ICP data drops; we can update these values ##
wb_2006 = td.constant_interp(wb_base_mapped, 2011, 2016, 2017)
wb_2018 = td.constant_interp(wb_base_mapped, 2022, 2024,2021)
wb_missing = td.interp_between(wb_base_mapped, 2017, 2021)
wb_2018 = td.interp_between(wb_base_mapped,2021,2024)
current_columns = wb_2018.columns.tolist()
new_first_column_name = 'RMM'
current_columns[0] = new_first_column_name
wb_2018.columns = current_columns
wb_2018 = wb_2018[['RMM','Category1','foo','Year','MARKET_CLASS','Value_x','pct','Method','ActEst']]
wb_2018 = wb_2018[wb_2018.Year > 2021]
wb_2018.to_csv('wb_2018_setup.csv')
wb_cs_yoy = pd.merge(wb_cs, map, how = 'inner', left_on = 'Market', right_on = 'MARKET').reset_index()
wb_cs_yoy = wb_cs_yoy[['RMM','Market','Year','CS_WB','CS_pct_WB','GDP_WB']]
for i in range(len(wb_cs_yoy)):
    if wb_cs_yoy.loc[i,'Year'] > 2021:
        if wb_cs_yoy.loc[i-1,'CS_WB'] > 0:
            wb_cs_yoy.loc[i,'cs_growth'] = (wb_cs_yoy.loc[i,'CS_WB']/wb_cs_yoy.loc[i-1,'CS_WB']) - 1
        else:
            pass

wb_2018 = pd.merge(wb_2018,wb_cs_yoy, how = 'left', left_on = ['RMM','Year'], right_on = ['RMM','Year'])
wb_2018.reset_index(inplace = True)
print(wb_2018.columns)
for i in range(len(wb_2018)):
    if wb_2018.loc[i,'Year'] > 2021:
        if math.isnan(wb_2018.loc[i,'cs_growth']):
            pass
        else:
            if wb_2018.loc[i,'Value_x'] > 0:
                wb_2018.loc[i,'Value_x'] = wb_2018.loc[i,'Value_x'] * (1 + wb_2018.loc[i,'cs_growth'])

wb_2018 = wb_2018[['RMM','Category1','foo','Year','MARKET_CLASS','Value_x','pct','Method','ActEst']]
wb_2018 = wb_2018[wb_2018.Year > 2021]
wb_base = td.intrp_act_merge(wb_2006,wb_2018,wb_missing)
wb_base = td.mrkt_bmrk(wb_base, wb_base)
wb_data = wb_base.copy()
wb_cs_int = pd.merge(wb_data,cs, how = 'outer', left_on = ['RMM','Year'],right_on = ['Market','Year']).reset_index()
wb_cs_int = wb_cs_int[['RMM','MARKET_CLASS','Category1','Year','Value_x','Method','ActEst','pct','Market','Value']]

# 2. Apply linear interpolation within each group
wb_cs_int["Value"] = wb_cs_int.groupby(['RMM','MARKET_CLASS'])["Value"].transform(
    lambda x: x.interpolate(method="linear",  limit_direction='both')
)

wb_rmm_bmrk = wb_cs_int.groupby(['RMM','MARKET_CLASS','Category1']).agg(
    cat_pct_rmm_bmrk = ('pct', 'mean')
).reset_index()

wb_class_bmrk = wb_cs_int.groupby(['MARKET_CLASS','Category1']).agg(
    cat_pct_class_bmrk = ('pct', 'mean')).reset_index()

wb_cs_int = pd.merge(wb_cs_int,wb_rmm_bmrk, how ='left', on = ['RMM','Category1'])
wb_cs_int.reset_index(inplace = True)
wb_cs_int = pd.merge(wb_cs_int,wb_class_bmrk, how ='outer', left_on = ['MARKET_CLASS_x','Category1'], right_on = ['MARKET_CLASS','Category1']).reset_index()

wb_cs_int['cat_pct_rmm_bmrk'] = np.where(pd.isna(wb_cs_int['cat_pct_rmm_bmrk']),wb_cs_int['cat_pct_class_bmrk'],wb_cs_int['cat_pct_rmm_bmrk'])
wb_cs_int['pct'] = np.where(pd.isna(wb_cs_int['pct']),wb_cs_int['cat_pct_rmm_bmrk'],wb_cs_int['pct'])
wb_cs_interp_check = wb_cs_int.groupby(['RMM','Year'])['pct'].sum().reset_index()
wb_cs_interp_check = pd.DataFrame(wb_cs_interp_check)
wb_cs_interp_check.columns =['RMM','Year','pct_fill']
wb_cs_interp_check['delta'] = (1 - wb_cs_interp_check['pct_fill'])/12.00
wb_cs_full = pd.merge(wb_cs_int,wb_cs_interp_check,how = 'left', on = ['RMM','Year'])
wb_cs_full.drop(columns = ['MARKET_CLASS_y','MARKET_CLASS','cat_pct_class_bmrk'], inplace = True)
wb_cs_full = wb_cs_full[wb_cs_full.RMM != 'Guatemala']
wb_cs_full['pct'] = wb_cs_full['pct'] + wb_cs_full['delta']
wb_cs_full['Value_x'] = np.where(pd.isna(wb_cs_full['Value_x']),wb_cs_full['pct'] * wb_cs_full['Value'],wb_cs_full['Value_x'])
wb_cs = pd.merge(wb_cs,map,how = 'inner', left_on = ['Market'], right_on = ['MARKET']).reset_index()
wb_cs.to_csv('check_map_wb_cs_GDP.csv')
wb_cs = wb_cs[['RMM','MARKET','Year','CS_WB','CS_pct_WB','GDP_WB']]
gdp = pd.read_csv('2026_updated_gdp_report_lcu.csv')
wb_cs = pd.merge(gdp,wb_cs, how ='left',left_on = ['RMM','YEAR'],right_on = ['RMM','Year'])
wb_cs_full = pd.merge(wb_cs_full,wb_cs, how = 'left', on = ['RMM','Year'])
wb_cs_full = wb_cs_full[wb_cs_full.NGDPD > 0]
wb_cs_full = wb_cs_full[['RMM','MARKET','MARKET_CLASS_x','Category1','Year','Value_x','Method','ActEst','pct','Market','Value','cat_pct_rmm_bmrk','pct_fill','delta','YEAR','NGDPD','CS_WB','CS_pct_WB','GDP_WB']]
wb_cs_full['NGDPD'] = wb_cs_full['NGDPD']/1000000000
wb_cs_full.reset_index(inplace = True)
wb_cs_backfill = wb_cs_full.groupby(['MARKET_CLASS_x','Year']).agg(
    cs_pct_gdp = ('CS_pct_WB','mean')
)
wb_cs_full = pd.merge(wb_cs_full,wb_cs_backfill, how = 'left', on = ['MARKET_CLASS_x','Year'])
wb_cs_full['CS_pct_WB'] = np.where(pd.isna(wb_cs_full['CS_pct_WB']),wb_cs_full['cs_pct_gdp'],wb_cs_full['CS_pct_WB'])
wb_cs_full['Value'] = np.where(pd.isna(wb_cs_full['Value']),wb_cs_full['CS_pct_WB'] * wb_cs_full['GDP_WB'] ,wb_cs_full['Value'])
wb_cs_full.to_csv('fill0_values_WB.csv')
wb_cs_full.reset_index(inplace = True)
for i in range(len(wb_cs_full)):
    if wb_cs_full.loc[i,'Value'] ==0:
        wb_cs_full.loc[i,'Value'] = wb_cs_full.loc[i,'CS_pct_WB'] * wb_cs_full.loc[i,'GDP_WB']

    else:
        pass

for i in range(len(wb_cs_full)):
    if wb_cs_full.loc[i,'ActEst'] == 'E':
        wb_cs_full.loc[i,'Value_x'] = wb_cs_full.loc[i,'pct'] * wb_cs_full.loc[i,'Value']

    else:
        pass
wb_cs_val_check = wb_cs_full.groupby(['RMM','Year']).agg(
    total_cs_bn= ('Value','mean'),
    cs_by_cat = ('Value_x','sum')
).reset_index()
wb_cs_full.rename(columns = {'MARKET_CLASS_x':'MARKET_CLASS'}, inplace = True)
for i in range(len(wb_cs_full)):
    if wb_cs_full.loc[i,'MARKET_CLASS'] == 'VERY HIGH INCOME':
        wb_cs_full.loc[i,'MARKET_CLASS'] = 'VERY HIGH INCOME'

    elif wb_cs_full.loc[i,'MARKET_CLASS'] in ('CARIBBEAN SMALL STATES - HIGHER INCOME','FCS - HIGHER INCOME','HIGH INCOME','PACIFIC ISLANDS - HIGHER INCOME'):
        wb_cs_full.loc[i,'MARKET_CLASS'] = 'HIGH INCOME'

    else:
        wb_cs_full.loc[i,'MARKET_CLASS'] = 'UPPER MID INCOME'

### ADD Code3 from COICOP ###
wb_data = pd.merge(wb_cs_full,hierarchy_wb_cs, how = 'left', on = ['Category1'])
wb_data = wb_data[['RMM','MARKET','MARKET_CLASS','Category1','Year','Value_x','Market','Value','NGDPD','GDP_WB','Transaction','Category2','Code1','Code2','Code3','Code4']]
wb_data = pd.merge(wb_data,weights, how = 'left', left_on = ['MARKET_CLASS','Code3'],right_on = ['MarketClass','Code'])
wb_data = wb_data[['RMM','MARKET','MARKET_CLASS','Category1','Year','Value_x','GDP_WB','NGDPD','Transaction','Category2','Code1','Code2','Code3','Code4','Weight','Product Category']]
wb_data.rename(columns = {'Product Category':'Product_Category3'}, inplace = True)

#### Add Code4 from COICOP ###
wb_data = pd.merge(wb_data,weights, how = 'left', left_on = ['MARKET_CLASS','Code4'],right_on = ['MarketClass','Code'])
wb_data.rename(columns = {'Product Category':'Product_Category4','Weight_x':'Weight_3','Weight_y':'Weight_4'}, inplace = True)
wb_data = wb_data[['RMM','MARKET','MARKET_CLASS','Category1','Year','Value_x','GDP_WB','NGDPD','Transaction','Category2','Code1','Code2','Code3','Weight_3','Product_Category3','Code4','Weight_4','Product_Category4']]

#cs_wb_l2 = pd.read_csv('WB_PLACEHOLDER_L2_coicop.csv')
############################################################
##### Benchmark Missing CS PCT by Category #####
############################################################
wb_bmrk_l2 = pd.DataFrame(cs_wb_l2[cs_wb_l2.LEVEL == 2]).groupby(['MARKET_CLASS','Year','coicop_1','coicop_2']).agg(cs_usd_base =('CS_USD_REBASE_L2','sum'))
wb_bmrk_l2.reset_index(inplace = True)
wb_bmrk_l1 = wb_bmrk_l2.groupby(['MARKET_CLASS','Year','coicop_1'])['cs_usd_base'].sum().reset_index()
wb_bmrk_l1.columns = ['MARKET_CLASS','Year','coicop_1','cs_l1_wb_base']
wb_bmrk_coicop = pd.merge(wb_bmrk_l2, wb_bmrk_l1, how = 'inner', on = ['MARKET_CLASS','Year','coicop_1'])
wb_data.to_csv('wb_cs_interp.csv')
wb_data = pd.merge(wb_data, wb_bmrk_coicop, how = 'left', left_on = ['MARKET_CLASS','Year','Code2'],right_on = ['MARKET_CLASS','Year','coicop_2'])
wb_data['code_2_pct'] = wb_data['cs_usd_base']/wb_data['cs_l1_wb_base']
wb_data['Code2_CS'] = wb_data['Value_x'] * wb_data['code_2_pct']
wb_data['Code2_CS'] = np.where(wb_data['Code2'].isin(['CP01','CP02','CP03','CP04','CP05','CP06','CP07','CP08','CP09','CP10','CP11','CP12','CP13']),wb_data['Value_x'],wb_data['Code2_CS'])
for i in range(len(wb_data)):
    if wb_data.loc[i,'Weight_3'] > 0.0:
        wb_data.loc[i,'Code3_CS'] = wb_data.loc[i,'Weight_3'] * wb_data.loc[i,'Code2_CS']
    else:
        pass

for i in range(len(wb_data)):
    if wb_data.loc[i,'Weight_4'] > 0.0:
        wb_data.loc[i,'Code4_CS'] = wb_data.loc[i,'Weight_4'] * wb_data.loc[i,'Code3_CS']
    else:
        pass

#pc_fw_map = pd.read_csv('pc_map_coicop_fw.csv')
wb_data1_2 = pd.merge(wb_data, pc_fw_map, how = 'inner', left_on = ['Code2'], right_on= ['CodeCategory'])
wb_data3 = pd.merge(wb_data, pc_fw_map, how = 'inner', left_on = ['Code3'], right_on= ['CodeCategory'])
wb_data4 = pd.merge(wb_data, pc_fw_map, how = 'inner', left_on = ['Code4'], right_on= ['CodeCategory'])

wb_data1_2 = wb_data1_2[['RMM','MARKET','MARKET_CLASS','Year','Value_x','GDP_WB','NGDPD','Transaction','Code1','Code2','Code3','Code4','Code2_CS','Product_Category','CodeCategory']]
wb_data1_2.reset_index(inplace = True)
wb_data1_2.columns = ['index','RMM','MARKET','MARKET_CLASS','Year','Value_x','GDP_WB','NGDPD','Transaction','Code1','Code2','Code3','Code4','PC_CS_LCU','Product_Category','CodeCategory']
wb_data1_2.to_csv('cat1cat2_map_test.csv')
wb_data3 = wb_data3[['RMM','MARKET','MARKET_CLASS','Year','Value_x','GDP_WB','NGDPD','Transaction','Code1','Code2','Code3','Code4','Code3_CS','Product_Category','CodeCategory']]
wb_data3.reset_index(inplace = True)
wb_data3.columns = ['index','RMM','MARKET','MARKET_CLASS','Year','Value_x','GDP_WB','NGDPD','Transaction','Code1','Code2','Code3','Code4','PC_CS_LCU','Product_Category','CodeCategory']
wb_data3.to_csv('cat3_map_test.csv')
wb_data4 = wb_data4[['RMM','MARKET','MARKET_CLASS','Year','Value_x','GDP_WB','NGDPD','Transaction','Code1','Code2','Code3','Code4','Code4_CS','Product_Category','CodeCategory']]
wb_data4.reset_index(inplace = True)
wb_data4.columns = ['index','RMM','MARKET','MARKET_CLASS','Year','Value_x','GDP_WB','NGDPD','Transaction','Code1','Code2','Code3','Code4','PC_CS_LCU','Product_Category','CodeCategory']
wb_data4.to_csv('cat4_map_test.csv')
wb_data_pc = pd.concat([wb_data1_2,wb_data3,wb_data4], axis = 0)
wb_data_pc = wb_data_pc.groupby(['RMM','MARKET','Year','Product_Category'])['PC_CS_LCU'].sum().reset_index()
wb_data_pc.columns = ['RMM','MARKET','Year','Product_Category','PC_SPEND_LCU']
wb_cs_total = wb_data_pc.groupby(['RMM','MARKET','Year']).agg(
    PC_SPEND_LCU = ('PC_SPEND_LCU','sum')
).reset_index()
wb_cs_total['Product_Category'] = 'Total_CS'
wb_cs_total =wb_cs_total[['RMM','MARKET','Year','Product_Category','PC_SPEND_LCU']]
wb_data_pc = pd.concat([wb_data_pc,wb_cs_total], axis = 0)
#### CONVERT CS from BILLIONS to MILLIONS to merge with EUROOECD DATA ####
wb_data_pc['PC_SPEND_LCU'] = 1000 * wb_data_pc['PC_SPEND_LCU']

#oecd_data = pd.read_csv('UK_cs_mapped_ROLLUP_FUNCTION.csv')
cs_fw = pd.merge(wb_data_pc, oecd_data, how = 'outer', on = ['RMM','Year','Product_Category'])
wb_rmms = pd.DataFrame(wb_data_pc['RMM'].drop_duplicates())
wb_rmms.columns = ['wb_available']
oecd_rmms = pd.DataFrame(oecd_data['RMM'].drop_duplicates())
oecd_rmms.columns = ['eurooecd_available']
fw_cs_rmms = pd.merge(wb_rmms,oecd_rmms, how = 'outer', left_on = 'wb_available', right_on = 'eurooecd_available')
fw_cs_rmms.reset_index(inplace = True)

for i in range(len(fw_cs_rmms)):
    if pd.isna(fw_cs_rmms.loc[i,'eurooecd_available']):
        fw_cs_rmms.loc[i,'use_flag'] = 1
    else:
        fw_cs_rmms.loc[i,'use_flag'] = 0

oecd_cs_rmms = fw_cs_rmms[fw_cs_rmms.use_flag == 0]
oecd_cs_data = pd.merge(oecd_data,oecd_cs_rmms, how = 'inner', left_on = 'RMM', right_on = 'eurooecd_available').reset_index()
oecd_cs_data.drop(columns = ['index','wb_available','eurooecd_available','use_flag','level_0'], inplace = True)
oecd_cs_data['api_flag'] = 'EUROOECD'
fw_cs_rmms = fw_cs_rmms[fw_cs_rmms.use_flag == 1]
wb_cs_data = pd.merge(wb_data_pc,fw_cs_rmms, how = 'inner', left_on = 'RMM', right_on = 'wb_available').reset_index()
wb_cs_data.drop(columns = ['index','wb_available','eurooecd_available','use_flag','level_0'], inplace = True)
wb_cs_data['api_flag'] = 'WORLD_BANK'
oecd_cs_data.reset_index(inplace = True)
oecd_cs_data.rename(columns = {'Market':'MARKET'}, inplace = True)
oecd_cs_data = oecd_cs_data[['RMM','MARKET','Year','Product_Category','PC_SPEND_LCU','api_flag']]
wb_cs_data = wb_cs_data[['RMM','MARKET','Year','Product_Category','PC_SPEND_LCU','api_flag']]
fw_cs_data = pd.concat([oecd_cs_data,wb_cs_data], axis = 0)
fw_cs_data.to_csv('fw_cs_check_data.csv')








