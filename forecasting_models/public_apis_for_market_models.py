import requests # Python 3.10
import pandas as pd
import download_data as dd

def pull_imf():
    # set URL for the IMF API
    url = 'https://www.imf.org/external/datamapper/api/v1/'
    key = 'NGDP_RPCH/NGDPD/PCPIPCH/LP/LUR'

    # these are the variables we'll use
    # NGDP_RPCH (GDP REAL GROWTH)
    # NGDPD (GDP IN USD)
    # PCPIPCH (CPI)
    # LP (POPULATION)
    # LUR (UNEMPLOYMENT)GDP

    # submit request
    response = requests.get(f'{url}{key}').json()

    # grab the first part of the dictionary and set to a new variable
    dt = list(response.values())[0]

    # convert dictionary to a data frame
    df = pd.DataFrame.from_dict({(i, j): dt[i][j] for i in dt.keys() for j in dt[i].keys()},
                                orient='index').reset_index()
    # update the column names
    df.rename(columns={'level_0': 'METRIC', 'level_1': 'MARKET'}, inplace=True)

    # correct market names, match them to the RMM
    mrkt = dd.mrkt_lkp()
    df = df.merge(mrkt, how='left', on='MARKET')

    df = df[df['RMM'].notna()]
    df.drop('CODE', axis=1, inplace=True)
    df.drop('MARKET', axis=1, inplace=True)
    df = df.drop_duplicates().reset_index(drop=True)

    # melt the data frame so years are in a column
    years = df.columns[2:].tolist()
    dm = pd.melt(df, id_vars=['METRIC', 'RMM'], value_vars=years, var_name='YEAR', value_name='Value')

    # pivot the data frame so the metrics become their own columns
    dp = dm.pivot(index=['RMM', 'YEAR'], columns='METRIC', values='Value').reset_index()

    dp['YEAR'] = pd.to_numeric(dp['YEAR'], errors='coerce')
    dp['LUR'] = 100 - dp['LUR']
    dp['LP'] = 1000000 * dp['LP']
    dp['NGDPD'] = 1000000000 * dp['NGDPD']

    dp.to_csv('dp.csv')

    return dp


def conv_gdp(df):
    forex = pd.read_csv('2026_new_exchange_rates_report_april.csv.csv')
    df = df.merge(forex, how='left', right_on=['Country', 'Year'], left_on=['RMM', 'YEAR'])

    df['NGDPD'] = df['NGDPD'] * df['ERI_rate']

    df.drop('Country', axis=1, inplace=True)
    df.drop('Year', axis=1, inplace=True)
    df.drop('IMF_rate', axis=1, inplace=True)
    df.drop('ERI_rate', axis=1, inplace=True)

    return df


def pull_wb():

    # pull GDP and consumer spending data from the World Bank
    df = wb.data.DataFrame(['NE.CON.PRVT.CN', 'NE.CON.PRVT.ZS', 'NY.GDP.MKTP.CN'], time=range(1980, 2022),
                           labels=True).reset_index()

    # create year column, rename columns and variables, and reduce data set to necessary years only
    df.drop(['Series', 'Country'], axis=1, inplace=True)
    df = pd.melt(df, id_vars=['economy', 'series'], var_name='Year')
    df = pd.pivot_table(df, values=['value'], index=['economy', 'Year'], columns=['series']).reset_index()
    df.columns = ['Market', 'Year', 'CS_WB', 'CS_pct_WB', 'GDP_WB']

    # convert number formats into percentages and millions
    df['CS_pct_WB'] = df['CS_pct_WB']/100
    df['GDP_WB'] = df['GDP_WB']/1000000
    df['CS_WB'] = df['CS_WB']/1000000

    # adjust year formatting
    df['Year'] = df['Year'].str.slice(2, 6)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

    for i in range(len(df)):
        if df.loc[i, 'Market'] == 'SOM':
            if df.loc[i, 'Year'] == 2013:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 19283.8
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 19283.8
            elif df.loc[i, 'Year'] == 2014:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 20230.9542
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 20230.9542
            elif df.loc[i, 'Year'] == 2015:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 22254.2525
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 22254.2525
            elif df.loc[i, 'Year'] == 2016:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 23061.785
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 23061.785
            elif df.loc[i, 'Year'] == 2017:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 23098.66
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 23098.66
            elif df.loc[i, 'Year'] == 2018:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 23954.1844
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 23954.1844
            elif df.loc[i, 'Year'] == 2019:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 25063.75
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 25063.75
            elif df.loc[i, 'Year'] == 2020:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 25761
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 25761
            elif df.loc[i, 'Year'] == 2021:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 26039.0096
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 26039.0096
            elif df.loc[i, 'Year'] == 2022:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 26039.0096
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 26039.0096
            elif df.loc[i, 'Year'] == 2023:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 28055
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 28055
            elif df.loc[i, 'Year'] == 2024:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 29932.23
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 29932.23
            elif df.loc[i, 'Year'] == 2025:
                df.loc[i, 'CS_WB'] = df.loc[i, 'CS_WB'] / 32435.66
                df.loc[i, 'GDP_WB'] = df.loc[i, 'GDP_WB'] / 32435.66
    df.to_csv('wb_cleaned.csv')
    return df

# pull data from Eurostat via API
def pull_euro(series, coicop_lkp):
    # call Eurostat API
    df = eurostat.get_data_df(series)
    df = df[df.unit == 'CP_MNAC']
    df.drop('unit', axis=1, inplace=True)

    # transform Eurostat GDP data into long format with specific variables we need
    if series == 'nama_10_gdp':

        # reduce data frame to only consumer spending and GDP variables
        df = df[df.na_item.isin(['P31_S14_S15', 'B1GQ'])]

        # create column for year, GDP, and consumer spending and rename the columns
        df = pd.melt(df, id_vars=['na_item', 'geo\\time'], var_name='Year')
        df = pd.pivot_table(df, values=['value'], index=['geo\\time', 'Year'], columns=['na_item']).reset_index()
        df.columns = ['Market', 'Year', 'GDP_EURO', 'CS_EURO']

        # calculate consumer spending share of GDP
        df['CS_pct_EURO'] = df['CS_EURO']/df['GDP_EURO']  # do we use this at all?

        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df.to_csv('euro_gdp_cleaned.csv')

    # transform Eurostat consumer spending data into long format with specific variables we need
    if series == 'nama_10_co3_p3':

        # align category ids by merging Eurostat consumer spending data with the Eurostat coicop lookup
        df = pd.merge(left=df, right=coicop_lkp, how='left', on='coicop')
        df.rename(columns={'geo\\time': 'Market'}, inplace=True)

        # create a column for year and rename the columns
        df = pd.melt(df, id_vars=['Market', 'coicop', 'description'], var_name='Year')
        df.columns = ['Market', 'coicop', 'Transaction', 'Year', 'CS_EURO']
        df.to_csv('euro_cs_cleaned.csv')
    return df
