import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from sklearn.model_selection import cross_val_score
import sklearn.metrics
import nba_eda_functions as nba

nba_data = nba.pull_player_view()
player_list = nba.pull_player_list()
nba_data = pd.DataFrame(nba_data)
player_list = pd.DataFrame(player_list)
player_list['PLAYER_NAME'] = player_list['FIRSTNAME'] + ' ' + player_list['LASTNAME']

nba_data = pd.merge(nba_data,player_list, how = 'inner', left_on = 'PLAYER_ID', right_on = 'PERSONID')
print(nba_data.columns)
nba_data.dropna(subset=['PLAYER_NAME_x'], inplace=True)


for i in range(len(nba_data)):
    if nba_data.loc[i,'GUARD'] == 1 & nba_data.loc[i, 'FORWARD'] == 1:
        nba_data.loc[i, 'POSITION'] = "G"
    elif nba_data.loc[i,'FORWARD'] == 1 & nba_data.loc[i, 'CENTER'] == 1:
        nba_data.loc[i, 'POSITION'] = "F"
    elif nba_data.loc[i,"GUARD"] == 1:
        nba_data.loc[i, "POSITION"] = "G"
    elif nba_data.loc[i,"FORWARD"] == 1:
        nba_data.loc[i, "POSITION"] = "F"
    elif nba_data.loc[i,"CENTER"] == 1:
        nba_data.loc[i, "POSITION"] = "C"
    else:
        nba_data.loc[i, "POSITION"] = "F"


season_stats = ['Total_Points','Total_Rebounds','Total_Assists','Total_Blocks','Total_Steals']
seasons = [2023,2024,2025,2026]

nba_data = nba_data.groupby(["POSITION","YEAR_SEASON"]).agg(
        Total_Points=('POINTS', 'sum'),
        Total_Rebounds=('TRB', 'sum'),
        Total_Assists=('ASSISTS', 'sum'),
        Total_Blocks=('BLOCKS', 'sum'),
        Total_Steals=('STEALS', 'sum')
        )

nba_data = pd.DataFrame(nba_data)
nba_data.reset_index(inplace = True)
nba_data.to_csv('check_player_rollup.csv')
for season in seasons:
    for j in season_stats:
        nba_data_season = nba_data[nba_data.YEAR_SEASON == season]
        plt.bar(nba_data_season['POSITION'], nba_data_season[j], color='skyblue', width=0.6)
        plt.title(f"Total Stats for {season}")
        plt.xlabel('Player Position')
        plt.ylabel(f" Season Statistics: {j}")
        plt.show()
