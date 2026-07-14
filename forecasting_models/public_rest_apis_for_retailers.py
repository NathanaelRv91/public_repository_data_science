import pandasdmx
import io
import pandas as pd
import requests

oecd_raw = requests.get('https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5A_T500,2.0/A.JPN.S14......XDC.V..?startPeriod>2018&dimensionAtObservation=AllDimensions&format=csvfilewithlabels')
df = pd.read_csv(io.StringIO(oecd_raw.text))
oecd_raw = pd.Series(oecd_raw)
## We can turn this into a dataframe to analyze with other reports from OECD or World Bank ##
japan_report = japan_report[japan_report.TIME_PERIOD >= 2019]

df = japan_report.copy()
## USE a list of all COICOP markets for iterations #
rmm = ['AUS','AUT','BEL','BGR','BRA','CAN','CHE','CHL','CMR','COL','CRI','CZE','DEU','DNK','ESP','EST','FIN','FRA','GBR','GRC','HKG','HRV','HUN','IDN','IRL','ISL','ISR','ITA','JPN','KOR','LTU','LUX','LVA','MEX','NLD','NOR','NZL','POL','PRT','ROU','RUS','SEN','SVK','SVN','SWE','TUR','USA']
start_year = 2019
## WE want a pre-covid AND post-covid 10 year model so we pull 2019 data through latest available year by market! ##
for i in rmm:
    try:
        oecd_raw = requests.get(f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5A_T500,2.0/A.{i}.S14......XDC.V..?startPeriod={start_year}&dimensionAtObservation=AllDimensions&format=csvfilewithlabels")
        df_new = pd.read_csv(io.StringIO(oecd_raw.text))
        oecd_raw = pd.Series(oecd_raw)
        ## We can turn this into a dataframe to analyze with other reports from OECD or World Bank ##
        df_main = pd.concat([df_main,df_new], axis = 0)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")

df_main.to_csv('updated_oecd_raw_api_transaction_data.csv')
