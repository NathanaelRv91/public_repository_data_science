import pandas as pd
import datetime
import numpy as np

all_time_data = pd.read_csv('all_time_player_statistics.csv')
all_time_data = pd.DataFrame(all_time_data)
all_time_data['Year_int'] = pd.to_datetime(all_time_data['gameDateTimeEst'])
all_time_data['Year_int'] = all_time_data['Year_int'].dt.year
year_list = all_time_data['Year_int'].unique().tolist()
year_list = pd.Series(year_list)
year_list.to_csv('year_list.csv')
