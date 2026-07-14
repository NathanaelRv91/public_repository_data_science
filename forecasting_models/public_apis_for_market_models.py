import requests # Python 3.6
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
