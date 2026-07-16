WITH player_list AS (
  
  SELECT * FROM {{source('team_sources','team_list')}}
  
) 

  SELECT * FROM player_list 
