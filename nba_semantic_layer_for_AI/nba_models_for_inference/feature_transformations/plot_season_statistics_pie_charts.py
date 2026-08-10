import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import nba_eda_functions as nba

#nba_data = nba.pull_player_view()
#player_list = nba.pull_player_list()
player_list = pd.read_csv('load_player_details.csv')
nba_data = pd.read_csv('load_player_statistics_fcast_view.csv')
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


nba_data = nba_data.groupby(["POSITION","YEAR_SEASON"]).agg(
        Total_Points=('POINTS', 'sum'),
        Total_Rebounds=('TRB', 'sum'),
        Total_Assists=('ASSISTS', 'sum'),
        Total_Blocks=('BLOCKS', 'sum'),
        Total_Steals=('STEALS', 'sum')
        )
nba_data = pd.DataFrame(nba_data)
nba_data.reset_index(inplace = True)


colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
seasons = [2023,2024,2025]
season_stats = ['Total_Points','Total_Rebounds','Total_Assists','Total_Blocks','Total_Steals']
for season in seasons:
    for j in season_stats:
        nba_season = nba_data[nba_data.YEAR_SEASON == season]
        sizes = nba_season[j]
        plt.pie(
            sizes,
            labels= nba_season['POSITION'],
            colors=colors,
            autopct='%1.1f%%',  # Formats percentages to 1 decimal place
            shadow=True,  # Adds a 3D shadow effect
            startangle=140  # Rotates the start of the chart
        )
        plt.title(f"Distribution of {j} by Position for {season} :")
        plt.show()
