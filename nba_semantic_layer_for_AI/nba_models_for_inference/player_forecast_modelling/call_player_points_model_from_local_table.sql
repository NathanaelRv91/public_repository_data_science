

SELECT player_id, 
full_name AS PLAYER_NAME, 
season, 
NBA_DB.REPORTS.player_forecasting!predict(player_id, season, steals, assists, rebounds, blocks, wins) AS player_forecast 
FROM NBA_DB.REPORTS.int_lakers_team_data

