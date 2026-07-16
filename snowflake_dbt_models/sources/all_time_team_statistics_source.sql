WITH team_statistics AS (
  
  SELECT * FROM {{source('nba_reporting_sources','all_time_team_statistics')}}
  
) 

  SELECT * FROM team_statistics
