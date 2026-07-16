WITH player_details AS (
  
  SELECT * FROM {{source('player_sources','player_details')}}
  
) 

  SELECT * FROM player_details
