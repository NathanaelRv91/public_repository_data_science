{{ config(materialized = 'view',
  tags = ['player_statistics'],
  cluster_by = ['player_id','is_active_player'])}}

WITH career_stats as (
  SELECT player_id,
    COUNT(DISTINCT player_team_id) AS teams_played_for,
    COUNT(DISTINCT YEAR_INT) AS seasons_played,
    SUM(games_played) AS games_played,
    SUM(games_won) AS career_wins,
  -- total stats --
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
    SUM(fg_attempts) as career_fga,
    SUM(fg_made) AS career_fgm,
    DIV0(SUM(fg_made),SUM(fg_attempts)) AS career_fg_pct,
    SUM(pt3_att) AS career_pt3_fga,
    SUM(pt3_fgm) AS career_pt3_fgm,
    DIV0(SUM(pt3_fgm),SUM(pt3_att)) AS career_3pt_pct,
    SUM(fta) as career_fta,
    SUM(ftm) AS career_ftm,
    DIV0(SUM(ftm),SUM(fta)) AS career_ft_pct

  FROM {{ ref('int_player_team_season_report')}}
  GROUP BY 1
  )

SELECT a.*,
    b.birthdate,
    b.bodyweightlbs,
    b.heightinches,
    b.firstname,
    b.lastname,
    b.firstname || ' ' || b.lastname AS full_name,
    CASE WHEN b.TOYEAR > 2025 THEN 'ACTIVE' ELSE 'RETIRED' END AS is_active_player,
    b.school,
    b.fromyear,
    b.draftround,
    b.draftnumber,
    b.jersey,
    CASE WHEN b.guard = 1 THEN 'YES' ELSE 'NO' END AS is_guard,
    CASE WHEN b.forward = 1 THEN 'YES' ELSE 'NO' END AS is_forward,
    CASE WHEN b.center = 1 THEN 'YES' ELSE 'NO' END AS is_center,
    CASE WHEN ((b.guard = 1 AND b.forward = 1) OR (b.guard = 1 AND b.center = 1) OR (b.forward = 1 AND b.center = 1)) THEN 'YES' ELSE 'NO' END AS plays_multiple_positions

FROM career_stats a
  JOIN {{ ref('player_details_source')}} b
      ON a.player_id = b.personid





