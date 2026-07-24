from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import pandas as pd
import numpy as np
import time
from nba_api.stats.endpoints import playergamelog
# Retrieve information for all NBA players
nba_players = players.get_players()

# Search for a player by name to get their ID
player_search = [player for player in nba_players if player['full_name'] == 'James Harden'][0]
#print (lebron)
print(f"{player_search['full_name']} player ID: {player_search['id']}")
