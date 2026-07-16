WITH team_details AS (
  
  SELECT * FROM {{source('team_sources','team_details')}}
  
) 

  SELECT * FROM team_details
