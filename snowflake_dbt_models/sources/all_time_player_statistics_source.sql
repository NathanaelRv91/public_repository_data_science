WITH player_stats AS (
  
  SELECT * FROM {{source('nba_reports','all_time_player_statistics')}}
  
) 

  SELECT * FROM player_stats 
