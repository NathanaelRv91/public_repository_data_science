import eurostat
import pandas as pd
import numpy as np
import wbgapi as wb
import requests
import datetime as dt
import sdmx
import download_data as dd
import io


def pull_euro_cs():
    coicop_lkp = pd.read_csv('coicop_lkp.csv')
    df = eurostat.get_data_df('nama_10_co3_p3')
    df = df[df.unit == 'CP_MNAC']
    df.drop('unit', axis=1, inplace=True)
    # align category ids by merging Eurostat consumer spending data with the Eurostat coicop lookup
    df = pd.merge(left=df, right=coicop_lkp, how='left', on='coicop')
    df.rename(columns={'geo\TIME_PERIOD': 'Market'}, inplace=True)

    # create a column for year and rename the columns
    df = pd.melt(df, id_vars=['Market', 'coicop', 'description'], var_name='Year')
    df.columns = ['Market', 'coicop', 'Transaction', 'Year', 'CS_EURO']
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df.reset_index(inplace=True)
    df = df[df['Year'].isin(
        [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])]
    df.to_csv('euro_cs_coicop_cleaned.csv')
    return df

def pull_euro_gdp():
    df = eurostat.get_data_df('nama_10_gdp')
    df = df[df.unit == 'CP_MNAC']
    df.drop('unit', axis=1, inplace=True)

    df = df[df.na_item.isin(['P31_S14_S15', 'B1GQ'])]
    # create column for year, GDP, and consumer spending and rename the columns
    df = pd.melt(df, id_vars=['na_item', 'geo\TIME_PERIOD'], var_name='Year')
    df = df[df.value != 'A']
    df = pd.pivot_table(df, values=['value'], index=['geo\TIME_PERIOD', 'Year'], columns=['na_item']).reset_index()
    df.columns = ['Market', 'Year', 'GDP_EURO', 'CS_EURO']
    # calculate consumer spending share of GDP
    df['CS_pct_EURO'] = df['CS_EURO'] / df['GDP_EURO']
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df.reset_index(inplace=True)
    df = df[df['Year'].isin(
        [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])]
    df.to_csv('euro_cs_gdp_cleaned.csv')
    return df

def pull_oecd_cs_1999():
    url_group = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5_T501,1.0/A.AUS+CAN+CHL+COL+CRI+ISL+MEX+NZL+NOR+GBR+USA+BRA+CMR+HKG+IDN+SEN+RUS.S14....._T+CP01+CP011+CP012+CP02+CP021+CP022+CP023+CP03+CP031+CP032+CP04+CP041+CP042+CP043+CP044+CP045+CP05+CP051+CP052+CP053+CP054+CP055+CP056+CP06+CP061+CP062+CP063+CP07+CP071+CP072+CP073+CP08+CP081+CP082+CP083+CP09+CP091+CP092+CP093+CP094+CP095+CP096+CP10+CP101+CP102+CP103+CP104+CP105+CP11+CP111+CP112+CP12+CP121+CP122+CP122_127+CP123+CP124+CP125+CP126+CP127.XDC.V..?startPeriod=2009&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
    oecd_raw = requests.get(url_group)
    api_data = pd.read_csv(io.StringIO(oecd_raw.text))
    api_data = pd.DataFrame(api_data)
    api_data = api_data[['REF_AREA', 'EXPENDITURE', 'Expenditure', 'TIME_PERIOD', 'OBS_VALUE']]
    api_data.columns = ['Market', 'Category', 'Transaction', 'Year', 'CS_OECD']
    api_data.to_csv('oecd_cs_coicop_noneuro_api_data.csv')
    return api_data

def pull_oecd_cs_2018():
    ## PULL GROUP 1 for CS by Purpose ##
    url_full = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5A_T501,2.0/A.BEL+CZE+DNK+EST+FIN+FRA+DEU+GRC+HUN+AUT.S14....._T+CP01+CP011+CP012+CP013+CP02+CP021+CP022+CP023+CP024+CP03+CP031+CP032+CP04+CP041+CP042+CP043+CP044+CP045+CP05+CP051+CP052+CP053+CP054+CP055+CP056+CP06+CP061+CP062+CP063+CP064+CP07+CP071+CP072+CP073+CP074+CP08+CP081+CP082+CP083+CP09+CP091+CP092+CP093+CP094+CP095+CP096+CP097+CP098+CP10+CP101+CP102+CP103+CP104+CP105+CP11+CP111+CP112+CP12+CP121+CP122+CP13+CP131+CP132+CP133+CP139.XDC.V..?startPeriod=2009&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
    oecd_raw = requests.get(url_full)
    api_data = pd.read_csv(io.StringIO(oecd_raw.text))
    api_data.to_csv('test_market_data_coicop_apis_2018_first_10.csv')
    api_data = pd.DataFrame(api_data)
    api_data = api_data[['REF_AREA', 'EXPENDITURE', 'Expenditure', 'TIME_PERIOD', 'OBS_VALUE']]
    api_data.columns = ['Market', 'Category', 'Transaction', 'Year', 'CS_OECD']
    api_data.to_csv('final_api_df_COICOP_group1.csv')
    api_data1 = api_data.copy()

    ## PULL GROUP 2 for CS by Purpose ##
    url_group_2 = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5A_T501,2.0/A.IRL+ISR+ITA+JPN+KOR+LVA+LTU+LUX+NLD+POL.S14....._T+CP01+CP011+CP012+CP013+CP02+CP021+CP022+CP023+CP024+CP03+CP031+CP032+CP04+CP041+CP042+CP043+CP044+CP045+CP05+CP051+CP052+CP053+CP054+CP055+CP056+CP06+CP061+CP062+CP063+CP064+CP07+CP071+CP072+CP073+CP074+CP08+CP081+CP082+CP083+CP09+CP091+CP092+CP093+CP094+CP095+CP096+CP097+CP098+CP10+CP101+CP102+CP103+CP104+CP105+CP11+CP111+CP112+CP12+CP121+CP122+CP13+CP131+CP132+CP133+CP139.XDC.V..?startPeriod=2009&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
    # url_full = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5A_T501,2.0/A.BEL+CZE+DNK+EST+FIN+FRA+DEU+GRC+HUN+AUT.S14....._T+CP01+CP011+CP012+CP013+CP02+CP021+CP022+CP023+CP024+CP03+CP031+CP032+CP04+CP041+CP042+CP043+CP044+CP045+CP05+CP051+CP052+CP053+CP054+CP055+CP056+CP06+CP061+CP062+CP063+CP064+CP07+CP071+CP072+CP073+CP074+CP08+CP081+CP082+CP083+CP09+CP091+CP092+CP093+CP094+CP095+CP096+CP097+CP098+CP10+CP101+CP102+CP103+CP104+CP105+CP11+CP111+CP112+CP12+CP121+CP122+CP13+CP131+CP132+CP133+CP139.XDC.V..?startPeriod=2018&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
    oecd_raw = requests.get(url_group_2)
    api_data = pd.read_csv(io.StringIO(oecd_raw.text))
    api_data.to_csv('test_market_data_coicop_apis_2018_second_10.csv')
    api_data = pd.DataFrame(api_data)
    api_data = api_data[['REF_AREA', 'EXPENDITURE', 'Expenditure', 'TIME_PERIOD', 'OBS_VALUE']]
    api_data.columns = ['Market', 'Category', 'Transaction', 'Year', 'CS_OECD']
    api_data.to_csv('final_api_df_COICOP_group2.csv')
    api_data2 = api_data.copy()

    ## PULL GROUP 3 for CS by Purpose ##
    # url_full = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5A_T501,2.0/A.BEL+CZE+DNK+EST+FIN+FRA+DEU+GRC+HUN+AUT.S14....._T+CP01+CP011+CP012+CP013+CP02+CP021+CP022+CP023+CP024+CP03+CP031+CP032+CP04+CP041+CP042+CP043+CP044+CP045+CP05+CP051+CP052+CP053+CP054+CP055+CP056+CP06+CP061+CP062+CP063+CP064+CP07+CP071+CP072+CP073+CP074+CP08+CP081+CP082+CP083+CP09+CP091+CP092+CP093+CP094+CP095+CP096+CP097+CP098+CP10+CP101+CP102+CP103+CP104+CP105+CP11+CP111+CP112+CP12+CP121+CP122+CP13+CP131+CP132+CP133+CP139.XDC.V..?startPeriod=2018&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
    url_group_3 = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5A_T501,2.0/A.PRT+SVK+SVN+ESP+SWE+CHE+TUR+BGR+HRV+ROU.S14....._T+CP01+CP011+CP012+CP013+CP02+CP021+CP022+CP023+CP024+CP03+CP031+CP032+CP04+CP041+CP042+CP043+CP044+CP045+CP05+CP051+CP052+CP053+CP054+CP055+CP056+CP06+CP061+CP062+CP063+CP064+CP07+CP071+CP072+CP073+CP074+CP08+CP081+CP082+CP083+CP09+CP091+CP092+CP093+CP094+CP095+CP096+CP097+CP098+CP10+CP101+CP102+CP103+CP104+CP105+CP11+CP111+CP112+CP12+CP121+CP122+CP13+CP131+CP132+CP133+CP139.XDC.V..?startPeriod=2009&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
    oecd_raw = requests.get(url_group_3)
    api_data = pd.read_csv(io.StringIO(oecd_raw.text))
    # api_data.to_csv('test_market_data_coicop_apis_2018_third_10.csv')
    api_data = pd.DataFrame(api_data)
    api_data = api_data[['REF_AREA', 'EXPENDITURE', 'Expenditure', 'TIME_PERIOD', 'OBS_VALUE']]
    api_data.columns = ['Market', 'Category', 'Transaction', 'Year', 'CS_OECD']
    api_data.to_csv('final_api_df_COICOP_group3.csv')
    api_data3 = api_data.copy()

    oecd_cs_2018 = pd.concat([api_data1, api_data2, api_data3], axis=0)
    return oecd_cs_2018

def pull_oecd_gdp():
    url_full = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE,2.0/A.AUT+BEL+CAN+CHL+COL+CRI+CZE+DNK+EST+FIN+FRA+DEU+GRC+HUN+ISL+IRL+ISR+ITA+JPN+KOR+LVA+LTU+LUX+MEX+NLD+NZL+NOR+POL+PRT+SVK+SVN+ESP+SWE+CHE+TUR+GBR+USA+EA20+EU+EU27_2020+ALB+ARG+BRA+BGR+CPV+CMR+CHN+HRV+CYP+GEO+HKG+IND+IDN+KAZ+MDG+MLT+MAR+MKD+ROU+RUS+SAU+SEN+SRB+SGP+ZAF+ZMB+AUS.......XDC.V..?startPeriod=2006&dimensionAtObservation=AllDimensions&format=csvfilewithlabels"

    oecd_raw = requests.get(url_full)
    api_data = pd.read_csv(io.StringIO(oecd_raw.text))
    # api_data.to_csv('test_market_data_cs_gdp_full_response_df.csv')
    api_data = pd.DataFrame(api_data)

    # api_data = api_data[api_data.TRANSACTION == 'B1GQ' | api_data['Institutional sector'] == 'Households']
    api_data = api_data[(api_data['Institutional sector'] == 'Households') | (api_data['TRANSACTION'] == 'B1GQ')]
    print(api_data.columns)
    api_data = api_data[['REF_AREA', 'TIME_PERIOD', 'TRANSACTION', 'OBS_VALUE']]
    pivoted_data = api_data.pivot(index=['REF_AREA', 'TIME_PERIOD'], columns='TRANSACTION',
                                  values='OBS_VALUE').reset_index()
    pivoted_data['CS_pct_OECD'] = (pivoted_data['P3'] / pivoted_data['B1GQ']).round(6)
    pivoted_data.columns = ['Market', 'Year', 'GDP_OECD', 'CS_OECD', 'CS_pct_OECD']
    pivoted_data = pivoted_data[['Market', 'Year', 'CS_OECD', 'GDP_OECD', 'CS_pct_OECD']]
    pivoted_data.to_csv('oecd_cs_gdp_cleaned_oct.csv')
    return pivoted_data

def pull_wb_cs_gdp():
    df = wb.data.DataFrame(['NE.CON.PRVT.CN', 'NE.CON.PRVT.ZS', 'NY.GDP.MKTP.CN'], time=range(2008, 2025),
                           labels=True).reset_index()

    # create year column, rename columns and variables, and reduce data set to necessary years only
    df.drop(['Series', 'Country'], axis=1, inplace=True)
    df = pd.melt(df, id_vars=['economy', 'series'], var_name='Year')
    df = pd.pivot_table(df, values=['value'], index=['economy', 'Year'], columns=['series']).reset_index()
    df.columns = ['Market', 'Year', 'CS_WB', 'CS_pct_WB', 'GDP_WB']

    # convert number formats into percentages and billions
    df['CS_pct_WB'] = df['CS_pct_WB'] / 100
    df['GDP_WB'] = df['GDP_WB'] / 1000000000
    df['CS_WB'] = df['CS_WB'] / 1000000000

    # adjust year formatting
    df['Year'] = df['Year'].str.slice(2, 6)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df[df['Year'].isin(
        [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])]
    df.to_csv('wb_cs_gdp_cleaned_oct.csv')
    return df

def build_pycharm_rates():
    IMF_DATA = sdmx.Client('IMF_DATA')

    data_msg = IMF_DATA.data(
        'WEO',
        key='*.NGDP.A',
        params={'startPeriod': 2009}
    )

    gdp_df = sdmx.to_pandas(data_msg)
    gdp_df.to_csv('gdp_lcu.csv')
    print(gdp_df.head())

    ##### Pull GDP in USD for all markets
    data_msg_usd = IMF_DATA.data(
        'WEO',
        key='*.NGDPD.A',
        params={'startPeriod': 2009}
    )

    gdp_df_usd = sdmx.to_pandas(data_msg_usd)
    gdp_df_usd.to_csv('gdp_usd.csv')

    ###################################
    # Build GDP Table for Python Model
    ###################################
    gdp_lcu = gdp_df
    gdp_usd = gdp_df_usd
    market_map = dd.mrkt_lkp()
    gdp_report = pd.merge(gdp_lcu, gdp_usd, how='inner', on=['TIME_PERIOD', 'COUNTRY'],
                          suffixes=['_lcu', '_usd']).reset_index()

    gdp_report = gdp_report[['TIME_PERIOD', 'COUNTRY', 'value_lcu', 'value_usd']]
    gdp_report['IMF_RATE'] = (gdp_report['value_lcu'] / gdp_report['value_usd']).round(6)
    gdp_report_full = pd.merge(gdp_report, market_map, how='left', left_on='COUNTRY', right_on='MARKET').reset_index()
    for i in range(len(gdp_report_full)):
        if gdp_report_full.loc[i, 'COUNTRY'] == 'TWN':
            gdp_report_full.loc[i, 'RMM'] = 'Taiwan'
        if gdp_report_full.loc[i, 'COUNTRY'] == 'KOS':
            gdp_report_full.loc[i, 'RMM'] = 'Kosovo'

    gdp_report_full = gdp_report_full[['RMM', 'TIME_PERIOD', 'IMF_RATE']]
    gdp_report_full['ERI_RATE'] = gdp_report['IMF_RATE']
    gdp_report_full.columns = ['Country', 'Year', 'IMF_RATE', 'ERI_RATE']
    gdp_report_full = gdp_report_full.dropna(subset=['Country'])
    gdp_report_full.to_csv('model_rates.csv')
    return gdp_report_full