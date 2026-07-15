WITH player_list AS (
  
  SELECT * FROM {{source('player_sources','player_list')}}
  
) 

  SELECT * FROM player_list 

