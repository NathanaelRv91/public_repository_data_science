WITH player_stats AS (
  
  SELECT * FROM {{source('nba_reporting_sources','all_time_player_statistics')}}
  
) 

  SELECT * FROM player_stats 
