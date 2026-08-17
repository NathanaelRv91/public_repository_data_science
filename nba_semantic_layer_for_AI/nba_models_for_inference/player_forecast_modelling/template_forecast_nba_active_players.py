import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt


player = pd.read_csv('NBA_DB_PLAYER_STATS.csv')
print(player.columns)
player['PLAYER_NAME'] = player['FIRST_NAME'] + ' ' + player['LAST_NAME']
player_data = player[['PLAYER_NAME','PLAYER_TEAM_NAME','YEAR_SEASON','BLOCKS','STEALS','ASSISTS','TRB','POINTS','FT_PCT','WIN']]


player_report = player_data.groupby(['PLAYER_NAME','YEAR_SEASON']).agg(
    points = ('POINTS','sum'),
    steals = ('STEALS','sum'),
    blocks=('BLOCKS', 'sum'),
    assists=('ASSISTS', 'sum'),
    rebounds=('TRB', 'sum'),
    wins=('WIN', 'sum')
).reset_index()
player_report.reset_index(inplace = True)

fcast_base = pd.read_csv('setup_player_fcast.csv')

player_bmark = player_report.groupby(['PLAYER_NAME']).agg(
points = ('points','mean'),
    steals = ('steals','mean'),
    blocks=('blocks', 'mean'),
    assists=('assists', 'mean'),
    rebounds=('rebounds', 'mean'),
    wins=('wins', 'mean'),
    last_season = ('YEAR_SEASON','max'),
    seasons = ('YEAR_SEASON','count')
).reset_index()

print(player_bmark.columns)
fcast_players = pd.merge(fcast_base, player_bmark, how = 'left', on = 'PLAYER_NAME')
fcast_players['last_season'].fillna(2025,inplace = True)
fcast_players = fcast_players[fcast_players.last_season == 2025]
fcast_players.drop(columns = ['Unnamed: 0','level_0'], inplace = True)
fcast_players.sort_values(by = 'PLAYER_ID', ascending = True)
fcast_players.reset_index(inplace = True)
fcast_players = pd.read_csv('nba_setup_final.csv')

for i in range(len(fcast_players)):
    if fcast_players.loc[i,'YEAR'] > 2025:
        if pd.isna(fcast_players.loc[i-1,'YEAR_SEASON']):
            pass
        else:
            fcast_players.loc[i,'steals_y'] = fcast_players.loc[i - 1,'steals_y']
            fcast_players.loc[i, 'blocks_y'] = fcast_players.loc[i - 1, 'blocks_y']
            fcast_players.loc[i, 'assists_y'] = fcast_players.loc[i - 1, 'assists_y']
            fcast_players.loc[i, 'rebounds_y'] = fcast_players.loc[i - 1, 'rebounds_y']
            fcast_players.loc[i, 'wins_y'] = fcast_players.loc[i - 1, 'wins_y']
            fcast_players.loc[i, 'PLAYER_NAME'] = fcast_players.loc[i - 1, 'PLAYER_NAME']
            fcast_players.loc[i, 'PLAYER_NAMES'] = fcast_players.loc[i - 1, 'PLAYER_NAMES']
            fcast_players.loc[i,'YEAR_SEASON'] = fcast_players.loc[i-1,'YEAR_SEASON'] + 1

fcast_players.dropna(subset = ['PLAYER_NAME'], inplace = True)
#fcast_players.to_csv('nba_model_final_SETUP.csv')
#PLAYER_ID', inplace = True)
#fcast_players.sort_values(by = 'PLAYER_ID', inplace = True)
fcast_players.reset_index(inplace = True)
for i in range(len(fcast_players)):
    if fcast_players.loc[i, 'YEAR'] > 2025:
        fcast_players.loc[i, 'steals_x'] = .7 * fcast_players.loc[i - 1, 'steals_x'] + .3 * fcast_players.loc[i,'steals_y']
        fcast_players.loc[i, 'blocks_x'] = .7 * fcast_players.loc[i - 1, 'blocks_x'] + .3 * fcast_players.loc[
            i, 'blocks_y']
        fcast_players.loc[i, 'assists_x'] = .7 * fcast_players.loc[i - 1, 'assists_x'] + .3 * fcast_players.loc[
            i, 'assists_y']
        fcast_players.loc[i, 'rebounds_x'] = .7 * fcast_players.loc[i - 1, 'rebounds_x'] + .3 * fcast_players.loc[
            i, 'rebounds_y']
        fcast_players.loc[i, 'wins_x'] = .7 * fcast_players.loc[i - 1, 'wins_x'] + .3 * fcast_players.loc[
            i, 'wins_y']

fcast_players.to_csv('nba_model_final_SETUP.csv')
