import pandas as pd
import numpy as np
import datetime as dt
import eurostat


def cs_bmrk_l3(euro_cs_3yr):
    """USE the last 3 years by RMM/COICOP to impute missing values with recent
    best CS available data: Benchmarks from COICOP """
    euro_cs_3yr_total = pd.DataFrame(
        euro_cs_3yr[(euro_cs_3yr.Year >= 2022) & (euro_cs_3yr.coicop == 'TOTAL') & (euro_cs_3yr.CS_USD > 0)].groupby(
            ['RMM'])['CS_USD'].mean())
    euro_cs_3yr_coicop = pd.DataFrame(
        euro_cs_3yr[(euro_cs_3yr.Year >= 2022) & (euro_cs_3yr.coicop != 'TOTAL')].groupby(['RMM', 'coicop'])[
            'CS_USD'].mean())
    euro_cs_3yr_coicop.reset_index(inplace=True)
    print(euro_cs_3yr_coicop.columns)
    euro_cs_3yr_coicop = pd.merge(euro_cs_3yr_coicop, euro_cs_3yr_total, how='left', on=['RMM'])
    euro_cs_3yr_coicop.columns = ['RMM', 'coicop', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR']
    euro_cs_3yr_coicop['CS_USD_3YR_PCT'] = euro_cs_3yr_coicop['CS_USD_COICOP_3YR'] / euro_cs_3yr_coicop[
        'CS_USD_TOT_3YR']
    euro_cs_3yr_coicop = euro_cs_3yr_coicop[euro_cs_3yr_coicop.RMM != 'United Kingdom']
    euro_cs_3yr_coicop = euro_cs_3yr_coicop[euro_cs_3yr_coicop.RMM != 'Kosovo']
    return euro_cs_3yr

def transform_oecd_coicop(oecd_map):
    """SDMX V1.0 & V2.0 Are different from the updated REST APIs from the OECD.
    We need to handle the 30 euro markets with new COICOP codes differently to merge with
    the current EUROSTAT CS report & 16 LATAM/NAM/ASIA RMMs from COICOP """
    for i in range(len(oecd_map)):
        ###### CP01-CP05 Clean ########
        if oecd_map.loc[i, 'Category'] == 'CP022':
            oecd_map.loc[i, 'Transaction'] = 'Tobacco'
        elif oecd_map.loc[i, 'Category'] == 'CP023':
            oecd_map.loc[i, 'Transaction'] = 'Alcohol production services'
        elif oecd_map.loc[i, 'Category'] == 'CP043':
            oecd_map.loc[i, 'Transaction'] = 'Maintenance and repair of the dwelling'
        elif oecd_map.loc[i, 'Category'] == 'CP051':
            oecd_map.loc[i, 'Transaction'] = 'Furniture and furnishings, carpets and other floor coverings'
        ###### CP06-07 Clean ########
        elif oecd_map.loc[i, 'Category'] == 'CP061':
            oecd_map.loc[i, 'Transaction'] = 'Medical products, appliances and equipment'
        elif oecd_map.loc[i, 'Category'] == 'CP062':
            oecd_map.loc[i, 'Transaction'] = 'Outpatient services'
        elif oecd_map.loc[i, 'Category'] == 'CP063':
            oecd_map.loc[i, 'Transaction'] = 'Hospital services'

        elif oecd_map.loc[i, 'Category'] == 'CP073':
            oecd_map.loc[i, 'Transaction'] = 'Transport services'
        ###### CP08 Clean ########
        elif oecd_map.loc[i, 'Category'] == 'CP08':
            oecd_map.loc[i, 'Transaction'] = 'Communication'
        elif oecd_map.loc[i, 'Category'] == 'CP081':
            oecd_map.loc[i, 'Transaction'] = 'Telephone and telefax equipment'
        elif oecd_map.loc[i, 'Category'] == 'CP082':
            oecd_map.loc[i, 'Transaction'] = 'Postal services'
        elif oecd_map.loc[i, 'Category'] == 'CP083':
            oecd_map.loc[i, 'Transaction'] = 'Telephone and telefax services'
        ###### CP09 Clean ########
        elif oecd_map.loc[i, 'Category'] == 'CP09':
            oecd_map.loc[i, 'Transaction'] = 'Recreation and culture'
        elif oecd_map.loc[i, 'Category'] == 'CP091':
            oecd_map.loc[i, 'Transaction'] = 'Audio-visual, photographic and information processing equipment'
        elif oecd_map.loc[i, 'Category'] == 'CP092':
            oecd_map.loc[i, 'Transaction'] = 'Other major durables for recreation and culture'
        elif oecd_map.loc[i, 'Category'] == 'CP093':
            oecd_map.loc[i, 'Transaction'] = 'Other recreational items and equipment, gardens and pets'
        elif oecd_map.loc[i, 'Category'] == 'CP094':
            oecd_map.loc[i, 'Transaction'] = 'Recreational and cultural services'
        elif oecd_map.loc[i, 'Category'] == 'CP095':
            oecd_map.loc[i, 'Transaction'] = 'Newspapers, books and stationery'
        elif oecd_map.loc[i, 'Category'] == 'CP096':
            oecd_map.loc[i, 'Transaction'] = 'Package holidays'
        elif oecd_map.loc[i, 'Category'] == 'CP097':
            oecd_map.loc[i, 'Transaction'] = 'Cultural goods'
        elif oecd_map.loc[i, 'Category'] == 'CP098':
            oecd_map.loc[i, 'Transaction'] = 'Cultural services'

            ###### CP10-11 Clean ########
        elif oecd_map.loc[i, 'Category'] == 'CP10':
            oecd_map.loc[i, 'Transaction'] = 'Education'
        elif oecd_map.loc[i, 'Category'] == 'CP101':
            oecd_map.loc[i, 'Transaction'] = 'Pre-primary and primary education'
        elif oecd_map.loc[i, 'Category'] == 'CP105':
            oecd_map.loc[i, 'Transaction'] = 'Education not definable by level'
        elif oecd_map.loc[i, 'Category'] == 'CP11':
            oecd_map.loc[i, 'Transaction'] = 'Restaurants and hotels'
        elif oecd_map.loc[i, 'Category'] == 'CP111':
            oecd_map.loc[i, 'Transaction'] = 'Catering services'
        ###### CP12-13 Clean ########
        elif oecd_map.loc[i, 'Category'] == 'CP12':
            oecd_map.loc[i, 'Transaction'] = 'Miscellaneous goods and services'
        elif oecd_map.loc[i, 'Category'] == 'CP121':
            oecd_map.loc[i, 'Transaction'] = 'Insurance'
        elif oecd_map.loc[i, 'Category'] == 'CP122':
            oecd_map.loc[i, 'Transaction'] = 'Financial services n.e.c.'
        elif oecd_map.loc[i, 'Category'] == 'CP13':
            oecd_map.loc[i, 'Transaction'] = 'Social protection'
        elif oecd_map.loc[i, 'Category'] == 'CP132':
            oecd_map.loc[i, 'Transaction'] = 'Personal effects'
        elif oecd_map.loc[i, 'Category'] == 'CP133':
            oecd_map.loc[i, 'Transaction'] = 'Other services n.e.c.'
        elif oecd_map.loc[i, 'Category'] == 'CP139':
            oecd_map.loc[i, 'Transaction'] = 'Prostitution; other services n.e.c.'
        elif oecd_map.loc[i, 'Category'] == '_T':
            oecd_map.loc[i, 'Category'] = 'TOTAL'

    for i in range(len(oecd_map)):
        ###### CP01-CP05 Clean ########
        if oecd_map.loc[i, 'Category'] == 'CP133':
            oecd_map.loc[i, 'Category'] = 'CP127'
        elif oecd_map.loc[i, 'Category'] == 'CP132':
            oecd_map.loc[i, 'Category'] = 'CP123'
        elif oecd_map.loc[i, 'Category'] == 'CP122':
            oecd_map.loc[i, 'Category'] = 'CP126'
        elif oecd_map.loc[i, 'Category'] == 'CP13':
            oecd_map.loc[i, 'Category'] = 'CP124'
        elif oecd_map.loc[i, 'Category'] == 'CP139':
            oecd_map.loc[i, 'Category'] = 'CP122_127'

        elif oecd_map.loc[i, 'Category'] == 'CP081':
            oecd_map.loc[i, 'Category'] = 'CP082'
        elif oecd_map.loc[i, 'Category'] == 'CP082':
            oecd_map.loc[i, 'Category'] = 'CP081'
        elif oecd_map.loc[i, 'Category'] == 'CP131':
            oecd_map.loc[i, 'Category'] = 'CP121'
        elif oecd_map.loc[i, 'Category'] == 'CP121':
            oecd_map.loc[i, 'Category'] = 'CP125'

    return oecd_map


def fix_euro_bmrk(euro_full_report):
    #euro_full_report = pd.DataFrame(euro_full_report)
    euro_full_report = euro_full_report[euro_full_report['RMM'].isin(['Turkey', 'Montenegro'])].reset_index()
    euro_full_report = euro_full_report[euro_full_report['Year'].isin([2023, 2024])].reset_index()
    #euro_full_report.drop(columns=['Unnamed: 0', 'level_0'], inplace=True)
    euro_full_report.sort_values(by=['RMM', 'COICOP', 'Year'], inplace=True)
    euro_full_report['CS_L2_SPLIT_LY'] = euro_full_report['CS_L2_SPLIT'].shift(1)

    for i in range(len(euro_full_report)):
        if pd.isna(euro_full_report.loc[i, 'CS_L2_SPLIT']) & (euro_full_report.loc[i, 'LEVEL'] == 2):
            euro_full_report.loc[i, 'CS_FILL'] = 1
            euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_L2_SPLIT_LY'] * euro_full_report.loc[
                i, 'CS_L1_USD']
            euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * euro_full_report.loc[i, 'IMF_rate']
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'COICOP', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR', 'CS_USD_3YR_PCT',
         'CS_COICOP_BMRK_PCT', 'LEVEL', 'coicop_1', 'coicop_2', 'CS_TOT_REAL_USD', 'CS_COICOP_BMRK_L1_PCT',
         'CS_COICOP_BMRK_L2_PCT', 'CS_L2_SPLIT', 'CS_USD_REBASE_L2', 'CS_L1_USD']]

    return euro_full_report

def oecd_template(oecd_cs,oecd_map):
    oecd_yrs = pd.DataFrame(oecd_cs[['Market', 'Year']].drop_duplicates())
    oecd_yrs['key'] = 1
    oecd_map['key'] = 1
    oecd_map.reset_index(inplace=True)
    template = pd.merge(oecd_yrs, oecd_map, how='outer', on='key')
    template.to_csv('test_full_oecd_map.csv')
    return template

def clean_wb_icp(src):
    df = src[src['Classification Code'].isin(['ZS', 'CN'])]
    df = pd.melt(df, id_vars=['Series Name', 'Series Code', 'Classification Name', 'Classification Code',
                              'Country Name', 'Country Code'])
    df['Year'] = df['variable'].str.slice(0, 4)
    df['YearSeries'] = str(df['Classification Code']) + '_' + str(df['Series Code']) + '_' + str(df['Year'])
    #df["value"].replace({"..": ""}, inplace=True)
    #df['value'] = pd.to_numeric(df['value'])
    df['Source'] = 'World Bank ICP'
    df.rename(columns={'Classification Name': 'Measure', 'Country Name': 'Market', 'Series Name': 'Series',
                       'value': 'Value', 'Country Code': 'Code'}, inplace=True)
    df = df[['Market', 'Code', 'Series', 'Value', 'Year', 'Source', 'Measure']]

    return df

def mrkt_map(src, market_map):
    df = pd.merge(left=src, right=market_map, how='left', left_on='Market', right_on='MARKET')
    df = df.sort_values(by=['RMM', 'Series', 'Year'])
    df = df[df['Measure'].isin(['Expenditure (local currency units, billions)'])]
    df = df[df['RMM'].notna()]
    df.drop(['Market','MARKET'], axis=1, inplace=True)
    df.rename(columns={'RMM': 'Market'}, inplace=True)
    df['Year'] = pd.to_numeric(df.Year)
    df = df.drop_duplicates()
    df = df[df['Year'].isin([2011,2017, 2021])]

    return df

def missing_calcs(src):
    # Identify markets where there is only one value and constant for the other year, so we have a complete dataset
    rename = pd.read_excel('Mapping_eurostat_OECD_to_Edge.xlsx', sheet_name='Renaming(live)')
    wb_base_mapped = pd.merge(left=src, right=rename, how='inner', left_on='Series', right_on='WB ICP')
    wb_base_mapped.drop(['Category1_Orig', 'Category2_Orig', 'Category3_Orig', 'Category4_Orig', 'WB ICP'], axis=1,
                        inplace=True)
    df_sum = wb_base_mapped.groupby(['Market']).agg(ct=('pct', 'count')).reset_index()

    df_sum = df_sum[df_sum.ct == 7]
    single_val = pd.merge(wb_base_mapped, df_sum, how='inner', on='Market')
    single_val = single_val.dropna(subset=['pct'])
    single_val = single_val[['Market', 'Series', 'pct', 'ct']]

    # merge pc shares into main df
    wb_base_mapped = pd.merge(left=wb_base_mapped, right=single_val, how='left', on=['Market', 'Series'])

    wb_base_mapped['pct_x'] = np.where(wb_base_mapped['ct'] == 7, wb_base_mapped['pct_y'], wb_base_mapped['pct_x'])
    # wb_base_mapped['RMM'] = wb_base_mapped['RMM'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode(
    #     'utf-8')

    # check sum and count of year/market/market grouping
    wb_agg = wb_base_mapped.groupby(['Year', 'RMM', 'MARKET_CLASS', 'MARKET_CLASS_v2'], dropna=True).agg(
        sum=('pct_x', 'sum'), ct=('pct_x', 'count')).reset_index()

    # break out additional 5 categories with estimates
    # these categories are missing from ICP, so we're estimating them
    # method of estimation is made up based on coefficients, non-linear function, and sum of all other cats
    wb_agg = wb_agg[(wb_agg.ct == 7) & (wb_agg['sum'] > 0.0)]
    wb_agg['Education'] = np.where(wb_agg['MARKET_CLASS'] == 'LOW INCOME', 0.005, 0.013)
    wb_agg['Health'] = 0.1327 * np.exp(-2.048 * wb_agg['sum'])
    wb_agg['Housing'] = 0.5109 * np.exp(-1.642 * wb_agg['sum'])
    wb_agg['MiscGoods'] = 0.3617 * np.exp(-2.359 * wb_agg['sum'])
    wb_agg['Recreation'] = 0.1637 * np.exp(-1.295 * wb_agg['sum'])
    wb_agg['CalcTot'] = wb_agg.iloc[:, -5:].sum(axis=1)

    # get total with total of 7 reported cats and 5 estimated cats
    wb_agg['Tot'] = wb_agg['CalcTot'] + wb_agg['sum']

    # put calculated cats into a column
    wb_melt = pd.melt(wb_agg, id_vars=['Year', 'RMM', 'MARKET_CLASS', 'CalcTot', 'Tot'],
                      value_vars=['Education', 'Health', 'Housing', 'MiscGoods', 'Recreation'], value_name='pct',
                      var_name='Category1').dropna()
    wb_melt.sort_values(by=['Year', 'RMM', 'Category1'], ascending=[True, True, True], inplace=True)

    # rebase shares when they don't add up to 1
    wb_melt['PctPct'] = wb_melt['pct'] / wb_melt['CalcTot']
    wb_melt['Diff'] = 1 - wb_melt['Tot']
    wb_melt['PctNew'] = (wb_melt['Diff'] * wb_melt['PctPct']) + wb_melt['pct']

    wb_melt = wb_melt[['Year', 'RMM', 'MARKET_CLASS', 'Category1', 'PctNew']]
    wb_melt.rename(columns={'PctNew': 'pct'}, inplace=True)
    wb_melt["Category1"].replace(
        {"Housing": "Housing, water, electricity, gas and other fuels", "MiscGoods": "Miscellaneous goods and services",
         "Recreation": "Recreation and culture"}, inplace=True)
    wb_melt['Method'] = 'C'
    wb_melt['ActEst'] = 'E'

    # join on the newly created vars and then utlise the combine first to infill the cat1's
    wb_base_mapped.rename(columns={'pct_x': 'pct'}, inplace=True)
    wb_base_mapped1 = pd.concat([wb_base_mapped,wb_melt],axis = 0)
    wb_base_mapped1.sort_values(by=['Year', 'RMM', 'Category1'], ascending=[True, True, True], inplace=True)
    wb_base_mapped1 = wb_base_mapped1[
        ['Year', 'RMM', 'MARKET_CLASS', 'Category1', 'ActEst', 'Method', 'pct', 'Value_x']]

    return wb_base_mapped1

def constant_interp(src, yr_st, yr_end, yr_act):
    yr_rng = range(yr_st, yr_end + 1)
    yr_df = pd.DataFrame(data=yr_rng, columns=['Year'])
    wb = src[src['Year'] == yr_act]
    wb = wb[['Year', 'RMM', 'MARKET_CLASS', 'Value_x', 'Category1', 'pct']]
    wb_dist = src[['RMM', 'Category1']].drop_duplicates()
    wb_dist = wb_dist.assign(foo=1).merge(yr_df.assign(foo=1))
    df = pd.merge(wb_dist, wb, how='left', on=['RMM', 'Category1'])
    df = df.drop_duplicates()
    df.drop(['Year_y'], axis=1, inplace=True)
    df.rename(columns={'Year_x': 'Year'}, inplace=True)
    df.sort_values(by=['RMM', 'Year', 'Category1'], ascending=[True, True, True], inplace=True)
    df['Method'] = 'I'
    df['ActEst'] = 'E'

    return df


# constant linear interpolation
def interp_between(src, yr_st, yr_end):
    yr_rng = range(yr_st, yr_end + 1)
    yr_df = pd.DataFrame(data=yr_rng, columns=['Year'])
    wb = src[['Year', 'RMM', 'Value_x', 'Category1', 'Method', 'pct']]
    wb_dist = src[['RMM', 'Category1', 'MARKET_CLASS']].drop_duplicates()
    wb_dist = wb_dist.assign(foo=1).merge(yr_df.assign(foo=1))
    df = pd.merge(wb_dist, wb, how='left', on=['RMM', 'Category1', 'Year'])
    df.sort_values(by=['RMM', 'Category1', 'Year'], ascending=[True, True, True], inplace=True)
    df['ActEst'] = np.where(df['Value_x'] > 0, 'A', 'E')
    df['Value_x'] = df['Value_x'].interpolate(method='linear', axis=0)
    df['pct'] = df['pct'].interpolate(method='linear', axis=0)
    df['Method'] = np.where((df['ActEst'] == 'E') & (df['Method'] != 'C'), 'I', df['Method'])
    df['Method'].replace({np.nan: ''}, inplace=True)

    return df

def intrp_act_merge(int_st, int_end, src):
    int_st = int_st[['RMM', 'MARKET_CLASS', 'Category1', 'Year', 'Value_x', 'Method', 'ActEst', 'pct']]
    int_end = int_end[['RMM', 'MARKET_CLASS', 'Category1', 'Year', 'Value_x', 'Method', 'ActEst', 'pct']]
    wb_calc = pd.concat([int_st,int_end], axis = 0)
    wb_calc.sort_values(by=['RMM', 'Category1', 'Year'], ascending=[True, True, True], inplace=True)
    wb_base = src[['RMM', 'MARKET_CLASS', 'Category1', 'Year', 'Value_x', 'Method', 'ActEst', 'pct']]
    wb_base = pd.concat([wb_base,wb_calc],axis = 0)
    wb_base.sort_values(by=['RMM', 'Year', 'Category1'], ascending=[True, True, True], inplace=True)

    return wb_base

def mrkt_bmrk(src, wb_base):
    # create benchmarks by the market class
    src.replace([np.inf, -np.inf], np.nan, inplace=True)
    wb_bmark = wb_base.dropna(subset=['pct'])

    # Remove any markets that have any negatives
    wb_bmark = wb_bmark[wb_bmark['pct'] > 0]

    # Ensure markets have all series populated - is this 11
    wb_bmark_chk = wb_bmark.groupby(['RMM']).agg(count=('pct', 'count')).reset_index()
    max_val = wb_bmark_chk['count'].max()
    wb_bmark_chk = wb_bmark_chk[wb_bmark_chk['count'] == max_val]

    # create a dataset which has only the markets that we are interested in
    # Now average the pct by market class so that we get some benchmarks
    wb_bmark_df = pd.merge(wb_bmark_chk, src, how='inner', on='RMM')
    wb_bmark_df_agg = wb_bmark_df.groupby(['MARKET_CLASS', 'Category1', 'Year']).agg(avg=('pct', 'mean')).reset_index()

    # label the markets that are qualifying & which aren't so that we know which ones to overwrite with benchmarks
    src = pd.merge(src, wb_bmark_chk, how='left', on='RMM')
    src = pd.merge(src, wb_bmark_df_agg, how='left', on=['MARKET_CLASS', 'Category1', 'Year'])

    # need to label which ones have been overwritten with a benchmark too
    src['Method'] = np.where(src['count'] != max_val, 'B', src['Method'])
    src['pct'] = np.where(src['Method'] == 'B', src['avg'], src['pct'])
    # output src to check out the markets getting this treatment

    # now need to calculate the additional categories for those markets that are all benchmarked
    # add in missing cats by benchmarking too
    pc_chk = src.groupby(['RMM', 'Year']).agg(count=('pct', 'count')).reset_index()
    pc_chk = pc_chk[pc_chk['count'] == 7]
    pc_calc = pd.merge(left=src, right=pc_chk, how='inner', on=['RMM', 'Year'])
    # Calc the totals so that we can calc the remaining categories and then append back
    pc_calc_agg = pc_calc.groupby(['Year', 'RMM', 'MARKET_CLASS'], dropna=True).agg(sum=('pct', 'sum'),
                                                                                    ct=('pct', 'count')).reset_index()
    pc_calc_agg['Education'] = np.where(pc_calc_agg['MARKET_CLASS'] == 'LOW INCOME', 0.005, 0.013)
    pc_calc_agg['Health'] = 0.1327 * np.exp(-2.048 * pc_calc_agg['sum'])
    pc_calc_agg['Housing'] = 0.5109 * np.exp(-1.642 * pc_calc_agg['sum'])
    pc_calc_agg['MiscGoods'] = 0.3617 * np.exp(-2.359 * pc_calc_agg['sum'])
    pc_calc_agg['Recreation'] = 0.1637 * np.exp(-1.295 * pc_calc_agg['sum'])
    pc_calc_agg['CalcTot'] = pc_calc_agg.iloc[:, -5:].sum(axis=1)
    pc_calc_agg['Tot'] = pc_calc_agg['CalcTot'] + pc_calc_agg['sum']
    pc_calc_melt = pd.melt(pc_calc_agg, id_vars=['Year', 'RMM', 'MARKET_CLASS', 'CalcTot', 'Tot'],
                           value_vars=['Education', 'Health', 'Housing', 'MiscGoods', 'Recreation'], value_name='pct',
                           var_name='Category1').dropna()
    pc_calc_melt.sort_values(by=['Year', 'RMM', 'Category1'], ascending=[True, True, True], inplace=True)
    pc_calc_melt['PctPct'] = pc_calc_melt['pct'] / pc_calc_melt['CalcTot']
    pc_calc_melt['Diff'] = 1 - pc_calc_melt['Tot']
    pc_calc_melt['PctNew'] = (pc_calc_melt['Diff'] * pc_calc_melt['PctPct']) + pc_calc_melt['pct']
    pc_calc_melt = pc_calc_melt[['Year', 'RMM', 'MARKET_CLASS', 'Category1', 'PctNew']]
    pc_calc_melt.rename(columns={'PctNew': 'pct'}, inplace=True)
    pc_calc_melt["Category1"].replace(
        {"Housing": "Housing, water, electricity, gas and other fuels", "MiscGoods": "Miscellaneous goods and services",
         "Recreation": "Recreation and culture"}, inplace=True)
    pc_calc_melt['Method'] = 'C'
    pc_calc_melt['ActEst'] = 'E'
    wb_base1 = pd.concat([src,pc_calc_melt],axis = 0)
    wb_base1.sort_values(by=['Year', 'RMM', 'Category1'], ascending=[True, True, True], inplace=True)

    return wb_base1

def wb_cs_rebase(wb_cs, wb_gdp):
    return wb_cs,wb_gdp

# function to calculate prod cat growth based on estimated coefficients and total CS YoY growth
def calc_prodcat(df, pc, a1, a2, cs_growth):
    df[pc + '_growth'] = a1 + a2 * df[cs_growth]

    return df