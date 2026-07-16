{{ config(materialized = 'table',
  tags = 'nba_career_stats')}}

WITH career_stats as (
  SELECT player_id, 
    COUNT(DISTINCT player_team_id) AS teams_played_for, 
    COUNT(DISTINCT YEAR_INT) AS seasons_played,
    SUM(games_played) AS games_played,
  -- total stats --
    SUM(games_played) AS games_played,
    SUM(min_played) AS min_played, 
    SUM(points) AS career_points, 
    SUM(trb) AS career_trb, 
    SUM(drb) AS career_drb, 
    SUM(orb) AS career_orb, 
    SUM(assists) AS career_assists, 
    SUM(blocks) AS career_blocks,
    SUM(turnovers) AS career_turnovers, 
    SUM(personal_fouls) AS personal_fouls,
  -- career shootint -- 
    SUM(fg_attemps) as career_fga, 
    SUM(fg_made) AS career_fgm, 
    DIV0(SUM(fg_made),SUM(fg_attempts)) AS career_fg_pct, 
    SUM(pt3_att) AS career_pt3_fga, 
    SUM(pt3_fgm) AS career_pt3_fgm, 
    DIV0(SUM(pt3_fgm),SUM(pt3_fga)) AS career_3pt_pct,
    
  
  


  )

SELECT a.*. 
    b.

  FROM career_stats a 
    JOIN {{ref('player_details_source')}} b
      ON a.player_id = b.personid





