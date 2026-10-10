import pandas as pd
import numpy as np
import datetime as dt
import transform_data as td



def build_eurostat_cs(euro_cs,euro_gdp,map,market_rates,classifications, coicop_bmrk):
    euro_cs = euro_cs[euro_cs.Year != 2025]
    euro_cs.reset_index(inplace=True)
    ### ANY L1/L2 missing values will get imputed by market class benchmark figures before merging with OECD reports ###
    euro_cs['flag'] = np.where(np.isnan(euro_cs['CS_EURO']), 1, 0)
    euro_cs = pd.merge(euro_cs, map, how='inner', left_on='Market', right_on='MARKET')
    euro_cs = pd.merge(euro_cs, market_rates, how='inner', left_on=['RMM', 'Year'], right_on=['Country', 'Year'])
    euro_cs['CS_USD'] = euro_cs['CS_EURO'] / euro_cs['IMF_rate']
    euro_cs = euro_cs[['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate']]
    euro_cs.rename(columns={'Year_x': 'Year'}, inplace=True)
    euro_cs = pd.merge(euro_cs, classifications, how='left', on='RMM').reset_index()
    euro_cs_3yr = euro_cs.copy()
    ####################################################################################################
    ## Capture real pct splits of total CS for known markets: for Annual COICOP Category Spend in USD ##
    ####################################################################################################
    euro_cs_real_tot = pd.DataFrame(
        euro_cs[euro_cs.coicop == 'TOTAL'].groupby(['MARKET_CLASS', 'RMM', 'Year'])['CS_USD'].sum()).reset_index()
    euro_cs_real_tot.columns = ['MARKET_CLASS', 'RMM', 'Year', 'CS_TOT_REAL_USD']
    ######################################################################
    ## Benchmark by Transaction for Annual COICOP Category Spend in USD ##
    ######################################################################
    euro_cs_bmrk = euro_cs.groupby(['MARKET_CLASS', 'Year', 'coicop']).agg(cs_usd_coicop_avg=('CS_USD', 'mean'),
                                                                           cs_usd_coicop_bmrk=('CS_USD', 'sum'))
    euro_cs_bmrk.reset_index(inplace=True)
    euro_cs_bmrk.columns = ['MARKET_CLASS', 'Year', 'coicop', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK']
    ######################################################################
    ## Benchmark by Transaction for Annual Total CS Spend in USD ##
    ######################################################################
    euro_total_cs_bmrk = pd.DataFrame(
        euro_cs[euro_cs.coicop == 'TOTAL'].groupby(['MARKET_CLASS', 'Year']).agg(CS_TOTAL_BMRK_USD=('CS_USD', 'sum'),
                                                                                 CS_TOTAL_AVG_USD=('CS_USD', 'mean')))
    euro_total_cs_bmrk.reset_index(inplace=True)
    euro_total_cs_bmrk.columns = ['MARKET_CLASS', 'Year', 'CS_TOTAL_BMRK_USD', 'CS_TOTAL_AVG_USD']
    euro_cs_bmrk = pd.merge(euro_cs_bmrk, euro_total_cs_bmrk, how='left', on=['MARKET_CLASS', 'Year'])

    ############################################################################
    ## MERGE CS for EURO Markets with Market Class USD Benchmarks from COICOP ##
    ############################################################################
    euro_cs = pd.merge(euro_cs, euro_cs_bmrk, how='inner', on=['Year', 'MARKET_CLASS', 'coicop'])
    euro_cs.reset_index(inplace=True)
    #############################################################################
    ## MERGE EURO TOTAL CS by RMM/Year to replace missing total benchmarks/values
    #############################################################################
    euro_full_report = pd.merge(euro_cs, euro_gdp, how='left', on=['Year', 'Market'])
    euro_full_report.rename(columns={'CS_EURO_x': 'CS_EURO', 'CS_EURO_y': 'CS_EURO_MSTR'}, inplace=True)
    euro_full_report['CS_MSTR_USD'] = euro_full_report['CS_EURO_MSTR'] / euro_full_report['IMF_rate']
    euro_full_report['GDP_USD'] = euro_full_report['GDP_EURO'] / euro_full_report['IMF_rate']
    euro_full_report.dropna(subset='CS_EURO_MSTR', inplace=True)
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD']]
    euro_full_report['CS_TOTAL_AVG_USD'] = np.where(euro_full_report['CS_TOTAL_AVG_USD'] > 0,
                                                    euro_full_report['CS_TOTAL_AVG_USD'],
                                                    euro_full_report['CS_MSTR_USD'])
    ############################################################################
    ## USE the last 3 yers by RMM/COICOP to impute missing values with recent
    ## best CS available data: Benchmarks from COICOP ##
    ############################################################################
    euro_cs_3yr_total = pd.DataFrame(
        euro_cs_3yr[(euro_cs_3yr.Year >= 2022) & (euro_cs_3yr.coicop == 'TOTAL') & (euro_cs_3yr.CS_USD > 0)].groupby(
            ['RMM'])['CS_USD'].mean())
    euro_cs_3yr_coicop = pd.DataFrame(
        euro_cs_3yr[(euro_cs_3yr.Year >= 2022) & (euro_cs_3yr.coicop != 'TOTAL')].groupby(['RMM', 'coicop'])[
            'CS_USD'].mean())
    euro_cs_3yr_coicop.reset_index(inplace=True)
    euro_cs_3yr_coicop = pd.merge(euro_cs_3yr_coicop, euro_cs_3yr_total, how='left', on=['RMM'])
    euro_cs_3yr_coicop.columns = ['RMM', 'coicop', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR']
    euro_cs_3yr_coicop['CS_USD_3YR_PCT'] = euro_cs_3yr_coicop['CS_USD_COICOP_3YR'] / euro_cs_3yr_coicop[
        'CS_USD_TOT_3YR']
    excluded_markets = ['United Kingdom', 'Kosovo']
    euro_cs_3yr_coicop = euro_cs_3yr_coicop[~euro_cs_3yr_coicop['RMM'].isin(excluded_markets)]
    euro_full_report = pd.merge(euro_full_report, euro_cs_3yr_coicop, how='left', on=['RMM', 'coicop']).reset_index()
    euro_full_report['CS_COICOP_BMRK_PCT'] = euro_full_report['CS_USD_COICOP_AVG'] / euro_full_report[
        'CS_TOTAL_AVG_USD']
    euro_full_report['level'] = np.where(euro_full_report['coicop'].isin(
        ['CP01', 'CP02', 'CP03', 'CP04', 'CP05', 'CP06', 'CP07', 'CP08', 'CP09', 'CP10', 'CP11', 'CP12', 'CP13']), 1, 2)

    euro_full_report = pd.merge(euro_full_report, coicop_bmrk, how='left', left_on='coicop', right_on='coicop_2')
    euro_full_report.reset_index(inplace=True)
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'flag'] == 1 & pd.isna(euro_full_report.loc[i, 'CS_USD_COICOP_3YR']):
            euro_full_report.loc[i, 'CS_USD_COICOP_3YR'] = euro_full_report.loc[i, 'CS_COICOP_BMRK_PCT'] * \
                                                           euro_full_report.loc[i, 'CS_MSTR_USD']
        elif pd.isna(euro_full_report.loc[i, 'coicop_1']):
            euro_full_report.loc[i, 'coicop_1'] = euro_full_report.loc[i, 'coicop']

    euro_full_report = pd.merge(euro_full_report, euro_cs_real_tot, how='left', on=['MARKET_CLASS', 'RMM', 'Year'])

    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'CS_TOT_REAL_USD'] == 0.00:
            euro_full_report.loc[i, 'CS_TOT_REAL_USD'] = euro_full_report.loc[i, 'CS_MSTR_USD']
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'flag'] == 1 & euro_full_report.loc[i, 'level'] == 1:
            if euro_full_report.loc[i, 'CS_USD_3YR_PCT'] > 0:
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_TOT_REAL_USD'] * euro_full_report.loc[
                    i, 'CS_USD_3YR_PCT']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * euro_full_report.loc[
                    i, 'IMF_rate']
            else:
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_TOT_REAL_USD'] * \
                                                    euro_full_report.loc[i, 'CS_COICOP_BMRK_PCT']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * \
                                                     euro_full_report.loc[i, 'IMF_rate']

    euro_full_report = euro_full_report[euro_full_report.Year >= 2009]
    euro_full_report['CS_COICOP_BMRK_PCT'] = np.where(pd.isna(euro_full_report['CS_COICOP_BMRK_PCT']),
                                                      euro_full_report['CS_USD_3YR_PCT'],
                                                      euro_full_report['CS_COICOP_BMRK_PCT'])
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR', 'CS_USD_3YR_PCT',
         'CS_COICOP_BMRK_PCT', 'level', 'coicop_1', 'coicop_2', 'CS_TOT_REAL_USD']]
    euro_full_report.reset_index(inplace=True)
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'level'] == 1 & pd.isna(euro_full_report.loc[i, 'coicop_1']):
            euro_full_report.loc[i, 'coicop_1'] = euro_full_report.loc[i, 'coicop']
        else:
            pass

    euro_level_2 = pd.DataFrame(euro_full_report[euro_full_report.level == 1])[
        ['RMM', 'Year', 'coicop', 'CS_USD', 'CS_COICOP_BMRK_PCT']]
    euro_level_2.columns = ['RMM', 'Year', 'coicop', 'CS_L1_USD', 'CS_COICOP_BMRK_L1_PCT']
    euro_full_report = pd.merge(euro_full_report, euro_level_2, how='left', left_on=['RMM', 'Year', 'coicop_1'],
                                right_on=['RMM', 'Year', 'coicop'])

    test_l2_group = pd.DataFrame(euro_full_report[euro_full_report.level == 2])
    test_l2_group = test_l2_group.groupby(['RMM', 'Year', 'level', 'coicop_1'])['CS_COICOP_BMRK_PCT'].sum()
    test_l2_group = pd.DataFrame(test_l2_group)
    test_l2_group.reset_index(inplace=True)
    test_l2_group.columns = ['RMM', 'Year', 'level', 'coicop_1', 'CS_COICOP_BMRK_L2_PCT']
    euro_full_report = pd.merge(euro_full_report, test_l2_group, how='left', left_on=['RMM', 'Year', 'coicop_1'],
                                right_on=['RMM', 'Year', 'coicop_1'])
    euro_full_report.reset_index(inplace=True)
    euro_full_report.drop(columns=['coicop_y', 'level_y'])

    euro_full_report['CS_L2_SPLIT'] = euro_full_report['CS_COICOP_BMRK_PCT'] / euro_full_report['CS_COICOP_BMRK_L2_PCT']
    euro_full_report['CS_USD_REBASE_L2'] = euro_full_report['CS_L2_SPLIT'] * euro_full_report['CS_L1_USD']

    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'level_x'] == 2:
            if pd.isna(euro_full_report.loc[i, 'CS_USD']):
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_USD_REBASE_L2']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * euro_full_report.loc[
                    i, 'IMF_rate']

    ############################################################
    ## FIX Missing BMRK for Upper Mid Income: Turkey/Montenegro
    ############################################################
    for i in range(len(euro_full_report)):
        if (euro_full_report.loc[i, 'level_x'] == 2) & (euro_full_report.loc[i, 'RMM'] in (['Turkey', 'Montenegro'])):
            if pd.isna(euro_full_report.loc[i, 'CS_USD']) & euro_full_report.loc[i, 'Year'] == 2024:
                print('found!')

    euro_full_report.replace([np.inf, -np.inf], np.nan, inplace=True)
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop_x', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR', 'CS_USD_3YR_PCT',
         'CS_COICOP_BMRK_PCT', 'level_x', 'coicop_1', 'coicop_2', 'CS_TOT_REAL_USD', 'CS_COICOP_BMRK_L1_PCT',
         'CS_COICOP_BMRK_L2_PCT', 'CS_L2_SPLIT', 'CS_USD_REBASE_L2', 'CS_L1_USD']]
    euro_full_report.rename(columns={'coicop_x': 'COICOP', 'level_x': 'LEVEL'}, inplace=True)
    #######################################################################
    ## CLEAN TURKEY/MONTENEGRO for Imputations on L2 for missing benchmarks
    #######################################################################
    euro_fix_rmms = td.fix_euro_bmrk(euro_full_report)
    exclude_rmms = ['Turkey', 'Montenegro']
    # Filter out multiple values at once
    euro_full_report = euro_full_report[~euro_full_report['RMM'].isin(exclude_rmms)]
    euro_full_report = pd.concat([euro_full_report, euro_fix_rmms], axis=0)
    euro_full_report.to_csv('cs_euro_analysis_FUNCTION.csv')
    return euro_full_report

def build_oecd_cs_1999(euro_cs,euro_gdp,map,classifications,market_rates,coicop_bmrk):
    euro_cs.rename(columns={'Category': 'coicop', 'CS_OECD': 'CS_EURO'}, inplace=True)
    euro_gdp.rename(columns={'CS_OECD': 'CS_EURO', 'CS_pct_OECD': 'CS_pct_EURO', 'GDP_OECD': 'GDP_EURO'}, inplace=True)
    euro_cs.reset_index(inplace=True)
    ### ANY L1/L2 missing values will get imputed by market class benchmark figures before merging with OECD reports ###
    euro_cs['flag'] = np.where(np.isnan(euro_cs['CS_EURO']), 1, 0)
    euro_cs = pd.merge(euro_cs, map, how='inner', left_on='Market', right_on='MARKET')
    euro_cs = pd.merge(euro_cs, market_rates, how='inner', left_on=['RMM', 'Year'], right_on=['Country', 'Year'])
    euro_cs['CS_USD'] = euro_cs['CS_EURO'] / euro_cs['IMF_rate']
    for i in range(len(euro_cs)):
        if euro_cs.loc[i, 'coicop'] == '_T':
            euro_cs.loc[i, 'coicop'] = 'TOTAL'

    euro_cs = euro_cs[['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate']]
    euro_cs.rename(columns={'Year_x': 'Year'}, inplace=True)
    euro_cs = pd.merge(euro_cs, classifications, how='left', on='RMM').reset_index()
    euro_cs_3yr = euro_cs.copy()
    euro_cs_list = pd.DataFrame(euro_cs[['RMM']].drop_duplicates())
    ####################################################################################################
    ## Capture real pct splits of total CS for known markets: for Annual COICOP Category Spend in USD ##
    ####################################################################################################
    euro_cs_real_tot = pd.DataFrame(
        euro_cs[euro_cs.coicop == 'TOTAL'].groupby(['MARKET_CLASS', 'RMM', 'Year'])['CS_USD'].sum()).reset_index()
    euro_cs_real_tot.columns = ['MARKET_CLASS', 'RMM', 'Year', 'CS_TOT_REAL_USD']
    ######################################################################
    ## Benchmark by Transaction for Annual COICOP Category Spend in USD ##
    ######################################################################
    euro_cs_bmrk = euro_cs.groupby(['MARKET_CLASS', 'Year', 'coicop']).agg(cs_usd_coicop_avg=('CS_USD', 'mean'),
                                                                           cs_usd_coicop_bmrk=('CS_USD', 'sum'))
    euro_cs_bmrk.reset_index(inplace=True)
    euro_cs_bmrk.columns = ['MARKET_CLASS', 'Year', 'coicop', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK']
    ######################################################################
    ## Benchmark by Transaction for Annual Total CS Spend in USD ##
    ######################################################################
    euro_total_cs_bmrk = pd.DataFrame(
        euro_cs[euro_cs.coicop == 'TOTAL'].groupby(['MARKET_CLASS', 'Year']).agg(CS_TOTAL_BMRK_USD=('CS_USD', 'sum'),
                                                                                 CS_TOTAL_AVG_USD=('CS_USD', 'mean')))
    euro_total_cs_bmrk.reset_index(inplace=True)
    euro_total_cs_bmrk.columns = ['MARKET_CLASS', 'Year', 'CS_TOTAL_BMRK_USD', 'CS_TOTAL_AVG_USD']
    euro_cs_bmrk = pd.merge(euro_cs_bmrk, euro_total_cs_bmrk, how='left', on=['MARKET_CLASS', 'Year'])
    ############################################################################
    ## MERGE CS for EURO Markets with Market Class USD Benchmarks from COICOP ##
    ############################################################################
    euro_cs = pd.merge(euro_cs, euro_cs_bmrk, how='inner', on=['Year', 'MARKET_CLASS', 'coicop'])
    euro_cs.reset_index(inplace=True)
    #############################################################################
    ## MERGE EURO TOTAL CS by RMM/Year to replace missing total benchmarks/values
    #############################################################################
    euro_full_report = pd.merge(euro_cs, euro_gdp, how='left', on=['Year', 'Market'])
    euro_full_report.rename(columns={'CS_EURO_x': 'CS_EURO', 'CS_EURO_y': 'CS_EURO_MSTR'}, inplace=True)
    euro_full_report['CS_MSTR_USD'] = euro_full_report['CS_EURO_MSTR'] / euro_full_report['IMF_rate']
    euro_full_report['GDP_USD'] = euro_full_report['GDP_EURO'] / euro_full_report['IMF_rate']
    euro_full_report.dropna(subset='CS_EURO_MSTR', inplace=True)
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD']]
    euro_full_report['CS_TOTAL_AVG_USD'] = np.where(euro_full_report['CS_TOTAL_AVG_USD'] > 0,
                                                    euro_full_report['CS_TOTAL_AVG_USD'],
                                                    euro_full_report['CS_MSTR_USD'])
    ############################################################################
    ## USE the last 3 yers by RMM/COICOP to impute missing values with recent
    ## best CS available data: Benchmarks from COICOP ##
    ############################################################################
    euro_cs_3yr_total = pd.DataFrame(
        euro_cs_3yr[(euro_cs_3yr.Year >= 2022) & (euro_cs_3yr.coicop == 'TOTAL') & (euro_cs_3yr.CS_USD > 0)].groupby(
            ['RMM'])['CS_USD'].mean())
    euro_cs_3yr_coicop = pd.DataFrame(
        euro_cs_3yr[(euro_cs_3yr.Year >= 2022) & (euro_cs_3yr.coicop != 'TOTAL')].groupby(['RMM', 'coicop'])[
            'CS_USD'].mean())
    euro_cs_3yr_coicop.reset_index(inplace=True)
    euro_cs_3yr_coicop = pd.merge(euro_cs_3yr_coicop, euro_cs_3yr_total, how='left', on=['RMM'])
    euro_cs_3yr_coicop.columns = ['RMM', 'coicop', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR']
    euro_cs_3yr_coicop['CS_USD_3YR_PCT'] = euro_cs_3yr_coicop['CS_USD_COICOP_3YR'] / euro_cs_3yr_coicop[
        'CS_USD_TOT_3YR']
    #included_markets = ['United Kingdom', 'United States', 'Mexico', 'Canada']
    #euro_cs_3yr_coicop = euro_cs_3yr_coicop[euro_cs_3yr_coicop['RMM'].isin(included_markets)]

    euro_full_report = pd.merge(euro_full_report, euro_cs_3yr_coicop, how='left', on=['RMM', 'coicop']).reset_index()
    euro_full_report['CS_COICOP_BMRK_PCT'] = euro_full_report['CS_USD_COICOP_AVG'] / euro_full_report[
        'CS_TOTAL_AVG_USD']
    euro_full_report['level'] = np.where(euro_full_report['coicop'].isin(
        ['CP01', 'CP02', 'CP03', 'CP04', 'CP05', 'CP06', 'CP07', 'CP08', 'CP09', 'CP10', 'CP11', 'CP12', 'CP13']), 1, 2)

    euro_full_report = pd.merge(euro_full_report, coicop_bmrk, how='left', left_on='coicop', right_on='coicop_2')
    euro_full_report.reset_index(inplace=True)
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'flag'] == 1 & pd.isna(euro_full_report.loc[i, 'CS_USD_COICOP_3YR']):
            euro_full_report.loc[i, 'CS_USD_COICOP_3YR'] = euro_full_report.loc[i, 'CS_COICOP_BMRK_PCT'] * \
                                                           euro_full_report.loc[i, 'CS_MSTR_USD']
        elif pd.isna(euro_full_report.loc[i, 'coicop_1']):
            euro_full_report.loc[i, 'coicop_1'] = euro_full_report.loc[i, 'coicop']

    euro_full_report = pd.merge(euro_full_report, euro_cs_real_tot, how='left', on=['MARKET_CLASS', 'RMM', 'Year'])

    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'CS_TOT_REAL_USD'] == 0.00:
            euro_full_report.loc[i, 'CS_TOT_REAL_USD'] = euro_full_report.loc[i, 'CS_MSTR_USD']
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'flag'] == 1 & euro_full_report.loc[i, 'level'] == 1:
            if euro_full_report.loc[i, 'CS_USD_3YR_PCT'] > 0:
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_TOT_REAL_USD'] * euro_full_report.loc[
                    i, 'CS_USD_3YR_PCT']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * euro_full_report.loc[
                    i, 'IMF_rate']
            else:
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_TOT_REAL_USD'] * \
                                                    euro_full_report.loc[i, 'CS_COICOP_BMRK_PCT']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * \
                                                     euro_full_report.loc[i, 'IMF_rate']

    euro_full_report = euro_full_report[euro_full_report.Year >= 2009]
    euro_full_report['CS_COICOP_BMRK_PCT'] = np.where(pd.isna(euro_full_report['CS_COICOP_BMRK_PCT']),
                                                      euro_full_report['CS_USD_3YR_PCT'],
                                                      euro_full_report['CS_COICOP_BMRK_PCT'])
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR', 'CS_USD_3YR_PCT',
         'CS_COICOP_BMRK_PCT', 'level', 'coicop_1', 'coicop_2', 'CS_TOT_REAL_USD']]
    euro_full_report.reset_index(inplace=True)
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'level'] == 1 & pd.isna(euro_full_report.loc[i, 'coicop_1']):
            euro_full_report.loc[i, 'coicop_1'] = euro_full_report.loc[i, 'coicop']
        else:
            pass

    euro_level_2 = pd.DataFrame(euro_full_report[euro_full_report.level == 1])[
        ['RMM', 'Year', 'coicop', 'CS_USD', 'CS_COICOP_BMRK_PCT']]
    euro_level_2.columns = ['RMM', 'Year', 'coicop', 'CS_L1_USD', 'CS_COICOP_BMRK_L1_PCT']
    euro_full_report = pd.merge(euro_full_report, euro_level_2, how='left', left_on=['RMM', 'Year', 'coicop_1'],
                                right_on=['RMM', 'Year', 'coicop'])

    test_l2_group = pd.DataFrame(euro_full_report[euro_full_report.level == 2])
    test_l2_group = test_l2_group.groupby(['RMM', 'Year', 'level', 'coicop_1'])['CS_COICOP_BMRK_PCT'].sum()
    test_l2_group = pd.DataFrame(test_l2_group)
    test_l2_group.reset_index(inplace=True)
    test_l2_group.columns = ['RMM', 'Year', 'level', 'coicop_1', 'CS_COICOP_BMRK_L2_PCT']
    euro_full_report = pd.merge(euro_full_report, test_l2_group, how='left', left_on=['RMM', 'Year', 'coicop_1'],
                                right_on=['RMM', 'Year', 'coicop_1'])
    euro_full_report.reset_index(inplace=True)
    euro_full_report.drop(columns=['coicop_y', 'level_y'])
    euro_full_report['CS_L2_SPLIT'] = euro_full_report['CS_COICOP_BMRK_PCT'] / euro_full_report['CS_COICOP_BMRK_L2_PCT']
    euro_full_report['CS_USD_REBASE_L2'] = euro_full_report['CS_L2_SPLIT'] * euro_full_report['CS_L1_USD']

    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'level_x'] == 2:
            if pd.isna(euro_full_report.loc[i, 'CS_USD']):
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_USD_REBASE_L2']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * euro_full_report.loc[
                    i, 'IMF_rate']

    euro_full_report.replace([np.inf, -np.inf], np.nan, inplace=True)
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop_x', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR', 'CS_USD_3YR_PCT',
         'CS_COICOP_BMRK_PCT', 'level_x', 'coicop_1', 'coicop_2', 'CS_TOT_REAL_USD', 'CS_COICOP_BMRK_L1_PCT',
         'CS_COICOP_BMRK_L2_PCT', 'CS_L2_SPLIT', 'CS_USD_REBASE_L2', 'CS_L1_USD']]
    euro_full_report.rename(columns={'coicop_x': 'COICOP', 'level_x': 'LEVEL'}, inplace=True)
    ################################################
    ## SELECT COLUMNS to Return Back into the model
    ################################################
    euro_full_report.to_csv('oecd_analysis_non_euro_FUNCTION.csv')
    return euro_full_report

def build_oecd_cs_2018(euro_cs,euro_gdp,map,classifications,market_rates):
    euro_cs = td.transform_oecd_coicop(euro_cs)
    oecd_map = pd.DataFrame(euro_cs[['Category', 'Transaction']].drop_duplicates())
    oecd_template = td.oecd_template(euro_cs, oecd_map)
    oecd_template = oecd_template[['Market', 'Year', 'Category', 'Transaction']]
    oecd_template.columns = ['Market', 'Year', 'COICOP_CS', 'Transaction_CS']
    oecd_template.reset_index(inplace=True)

    euro_cs.rename(columns={'Category': 'coicop', 'CS_OECD': 'CS_EURO'}, inplace=True)
    euro_gdp.rename(columns={'CS_OECD': 'CS_EURO', 'CS_pct_OECD': 'CS_pct_EURO', 'GDP_OECD': 'GDP_EURO'}, inplace=True)
    euro_cs.reset_index(inplace=True)
    euro_cs = pd.merge(oecd_template, euro_cs, how='left', left_on=['Market', 'Year', 'COICOP_CS'],
                       right_on=['Market', 'Year', 'coicop'])
    euro_cs.reset_index(inplace=True)
    euro_cs = euro_cs[['Market', 'Year', 'COICOP_CS', 'Transaction_CS', 'CS_EURO']]
    euro_cs.columns = ['Market', 'Year', 'coicop', 'Transaction', 'CS_EURO']

    ### ANY L1/L2 missing values will get imputed by market class benchmark figures before merging with OECD reports ###
    euro_cs['flag'] = np.where(np.isnan(euro_cs['CS_EURO']), 1, 0)
    euro_cs = pd.merge(euro_cs, map, how='inner', left_on='Market', right_on='MARKET')
    euro_cs = pd.merge(euro_cs, market_rates, how='inner', left_on=['RMM', 'Year'], right_on=['Country', 'Year'])
    euro_cs['CS_USD'] = euro_cs['CS_EURO'] / euro_cs['IMF_rate']
    euro_cs = euro_cs[['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate']]
    euro_cs.rename(columns={'Year_x': 'Year'}, inplace=True)
    euro_cs = pd.merge(euro_cs, classifications, how='left', on='RMM').reset_index()
    euro_cs_3yr = euro_cs.copy()
    ####################################################################################################
    ## Capture real pct splits of total CS for known markets: for Annual COICOP Category Spend in USD ##
    ####################################################################################################
    euro_cs_real_tot = pd.DataFrame(
        euro_cs[euro_cs.coicop == 'TOTAL'].groupby(['MARKET_CLASS', 'RMM', 'Year'])['CS_USD'].sum()).reset_index()
    # euro_cs_real_tot.reset_index(inplace = True)
    euro_cs_real_tot.columns = ['MARKET_CLASS', 'RMM', 'Year', 'CS_TOT_REAL_USD']
    ######################################################################
    ## Benchmark by Transaction for Annual COICOP Category Spend in USD ##
    ######################################################################
    euro_cs_bmrk = euro_cs.groupby(['MARKET_CLASS', 'Year', 'coicop']).agg(cs_usd_coicop_avg=('CS_USD', 'mean'),
                                                                           cs_usd_coicop_bmrk=('CS_USD', 'sum'))
    euro_cs_bmrk.reset_index(inplace=True)
    euro_cs_bmrk.columns = ['MARKET_CLASS', 'Year', 'coicop', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK']
    ######################################################################
    ## Benchmark by Transaction for Annual Total CS Spend in USD ##
    ######################################################################
    euro_total_cs_bmrk = pd.DataFrame(
        euro_cs[euro_cs.coicop == 'TOTAL'].groupby(['MARKET_CLASS', 'Year']).agg(CS_TOTAL_BMRK_USD=('CS_USD', 'sum'),
                                                                                 CS_TOTAL_AVG_USD=('CS_USD', 'mean')))
    euro_total_cs_bmrk.reset_index(inplace=True)
    euro_total_cs_bmrk.columns = ['MARKET_CLASS', 'Year', 'CS_TOTAL_BMRK_USD', 'CS_TOTAL_AVG_USD']
    euro_cs_bmrk = pd.merge(euro_cs_bmrk, euro_total_cs_bmrk, how='left', on=['MARKET_CLASS', 'Year'])
    ############################################################################
    ## MERGE CS for EURO Markets with Market Class USD Benchmarks from COICOP ##
    ############################################################################
    euro_cs = pd.merge(euro_cs, euro_cs_bmrk, how='inner', on=['Year', 'MARKET_CLASS', 'coicop'])
    euro_cs.reset_index(inplace=True)
    #############################################################################
    ## MERGE EURO TOTAL CS by RMM/Year to replace missing total benchmarks/values
    #############################################################################
    euro_full_report = pd.merge(euro_cs, euro_gdp, how='left', on=['Year', 'Market'])
    euro_full_report.rename(columns={'CS_EURO_x': 'CS_EURO', 'CS_EURO_y': 'CS_EURO_MSTR'}, inplace=True)
    euro_full_report['CS_MSTR_USD'] = euro_full_report['CS_EURO_MSTR'] / euro_full_report['IMF_rate']
    euro_full_report['GDP_USD'] = euro_full_report['GDP_EURO'] / euro_full_report['IMF_rate']
    euro_full_report.dropna(subset='CS_EURO_MSTR', inplace=True)
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD']]
    euro_full_report['CS_TOTAL_AVG_USD'] = np.where(euro_full_report['CS_TOTAL_AVG_USD'] > 0,
                                                    euro_full_report['CS_TOTAL_AVG_USD'],
                                                    euro_full_report['CS_MSTR_USD'])
    ############################################################################
    ## USE the last 3 yers by RMM/COICOP to impute missing values with recent
    ## best CS available data: Benchmarks from COICOP ##
    ############################################################################
    euro_cs_3yr_total = pd.DataFrame(
        euro_cs_3yr[(euro_cs_3yr.Year >= 2022) & (euro_cs_3yr.coicop == 'TOTAL') & (euro_cs_3yr.CS_USD > 0)].groupby(
            ['RMM'])['CS_USD'].mean())
    euro_cs_3yr_coicop = pd.DataFrame(
        euro_cs_3yr[(euro_cs_3yr.Year >= 2022) & (euro_cs_3yr.coicop != 'TOTAL')].groupby(['RMM', 'coicop'])[
            'CS_USD'].mean())
    euro_cs_3yr_coicop.reset_index(inplace=True)
    euro_cs_3yr_coicop = pd.merge(euro_cs_3yr_coicop, euro_cs_3yr_total, how='left', on=['RMM'])
    euro_cs_3yr_coicop.columns = ['RMM', 'coicop', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR']
    euro_cs_3yr_coicop['CS_USD_3YR_PCT'] = euro_cs_3yr_coicop['CS_USD_COICOP_3YR'] / euro_cs_3yr_coicop[
        'CS_USD_TOT_3YR']

    euro_full_report = pd.merge(euro_full_report, euro_cs_3yr_coicop, how='left', on=['RMM', 'coicop']).reset_index()
    euro_full_report['CS_COICOP_BMRK_PCT'] = euro_full_report['CS_USD_COICOP_AVG'] / euro_full_report[
        'CS_TOTAL_AVG_USD']
    euro_full_report['level'] = np.where(euro_full_report['coicop'].isin(
        ['CP01', 'CP02', 'CP03', 'CP04', 'CP05', 'CP06', 'CP07', 'CP08', 'CP09', 'CP10', 'CP11', 'CP12', 'CP13']), 1, 2)
    coicop_bmrk = pd.read_csv('coicop_bmrk.csv')

    euro_full_report = pd.merge(euro_full_report, coicop_bmrk, how='left', left_on='coicop', right_on='coicop_2')
    euro_full_report.reset_index(inplace=True)
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'flag'] == 1 & pd.isna(euro_full_report.loc[i, 'CS_USD_COICOP_3YR']):
            euro_full_report.loc[i, 'CS_USD_COICOP_3YR'] = euro_full_report.loc[i, 'CS_COICOP_BMRK_PCT'] * \
                                                           euro_full_report.loc[i, 'CS_MSTR_USD']
        elif pd.isna(euro_full_report.loc[i, 'coicop_1']):
            euro_full_report.loc[i, 'coicop_1'] = euro_full_report.loc[i, 'coicop']

    euro_full_report = pd.merge(euro_full_report, euro_cs_real_tot, how='left', on=['MARKET_CLASS', 'RMM', 'Year'])

    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'CS_TOT_REAL_USD'] == 0.00:
            euro_full_report.loc[i, 'CS_TOT_REAL_USD'] = euro_full_report.loc[i, 'CS_MSTR_USD']
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'flag'] == 1 & euro_full_report.loc[i, 'level'] == 1:
            if euro_full_report.loc[i, 'CS_USD_3YR_PCT'] > 0:
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_TOT_REAL_USD'] * euro_full_report.loc[
                    i, 'CS_USD_3YR_PCT']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * euro_full_report.loc[
                    i, 'IMF_rate']
            else:
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_TOT_REAL_USD'] * \
                                                    euro_full_report.loc[i, 'CS_COICOP_BMRK_PCT']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * \
                                                     euro_full_report.loc[i, 'IMF_rate']

    euro_full_report = euro_full_report[euro_full_report.Year >= 2009]
    euro_full_report['CS_COICOP_BMRK_PCT'] = np.where(pd.isna(euro_full_report['CS_COICOP_BMRK_PCT']),
                                                      euro_full_report['CS_USD_3YR_PCT'],
                                                      euro_full_report['CS_COICOP_BMRK_PCT'])
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR', 'CS_USD_3YR_PCT',
         'CS_COICOP_BMRK_PCT', 'level', 'coicop_1', 'coicop_2', 'CS_TOT_REAL_USD']]
    euro_full_report.reset_index(inplace=True)
    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'level'] == 1 & pd.isna(euro_full_report.loc[i, 'coicop_1']):
            euro_full_report.loc[i, 'coicop_1'] = euro_full_report.loc[i, 'coicop']
        else:
            pass

    euro_level_2 = pd.DataFrame(euro_full_report[euro_full_report.level == 1])[
        ['RMM', 'Year', 'coicop', 'CS_USD', 'CS_COICOP_BMRK_PCT']]
    euro_level_2.columns = ['RMM', 'Year', 'coicop', 'CS_L1_USD', 'CS_COICOP_BMRK_L1_PCT']
    euro_full_report = pd.merge(euro_full_report, euro_level_2, how='left', left_on=['RMM', 'Year', 'coicop_1'],
                                right_on=['RMM', 'Year', 'coicop'])

    test_l2_group = pd.DataFrame(euro_full_report[euro_full_report.level == 2])
    test_l2_group = test_l2_group.groupby(['RMM', 'Year', 'level', 'coicop_1'])['CS_COICOP_BMRK_PCT'].sum()
    test_l2_group = pd.DataFrame(test_l2_group)
    test_l2_group.reset_index(inplace=True)
    test_l2_group.columns = ['RMM', 'Year', 'level', 'coicop_1', 'CS_COICOP_BMRK_L2_PCT']
    euro_full_report = pd.merge(euro_full_report, test_l2_group, how='left', left_on=['RMM', 'Year', 'coicop_1'],
                                right_on=['RMM', 'Year', 'coicop_1'])
    euro_full_report.reset_index(inplace=True)
    euro_full_report.drop(columns=['coicop_y', 'level_y'])
    euro_full_report['CS_L2_SPLIT'] = euro_full_report['CS_COICOP_BMRK_PCT'] / euro_full_report['CS_COICOP_BMRK_L2_PCT']
    euro_full_report['CS_USD_REBASE_L2'] = euro_full_report['CS_L2_SPLIT'] * euro_full_report['CS_L1_USD']

    for i in range(len(euro_full_report)):
        if euro_full_report.loc[i, 'level_x'] == 2:
            if pd.isna(euro_full_report.loc[i, 'CS_USD']):
                euro_full_report.loc[i, 'CS_USD'] = euro_full_report.loc[i, 'CS_USD_REBASE_L2']
                euro_full_report.loc[i, 'CS_EURO'] = euro_full_report.loc[i, 'CS_USD'] * euro_full_report.loc[
                    i, 'IMF_rate']

    euro_full_report.replace([np.inf, -np.inf], np.nan, inplace=True)
    euro_full_report = euro_full_report[
        ['RMM', 'Market', 'Year', 'coicop_x', 'Transaction', 'CS_EURO', 'CS_USD', 'flag', 'IMF_rate', 'MARKET_CLASS',
         'MARKET_CLASS_v2', 'CS_USD_COICOP_AVG', 'CS_USD_COICOP_BMRK', 'CS_TOTAL_AVG_USD', 'GDP_EURO', 'CS_EURO_MSTR',
         'CS_pct_EURO', 'CS_MSTR_USD', 'GDP_USD', 'CS_USD_COICOP_3YR', 'CS_USD_TOT_3YR', 'CS_USD_3YR_PCT',
         'CS_COICOP_BMRK_PCT', 'level_x', 'coicop_1', 'coicop_2', 'CS_TOT_REAL_USD', 'CS_COICOP_BMRK_L1_PCT',
         'CS_COICOP_BMRK_L2_PCT', 'CS_L2_SPLIT', 'CS_USD_REBASE_L2', 'CS_L1_USD']]
    euro_full_report.rename(columns={'coicop_x': 'COICOP', 'level_x': 'LEVEL'}, inplace=True)
    ################################################
    ## SELECT COLUMNS to Return Back into the model
    ################################################
    euro_full_report.to_csv('oecd_analysis_euro_new_FUNCTION.csv')
    return euro_full_report