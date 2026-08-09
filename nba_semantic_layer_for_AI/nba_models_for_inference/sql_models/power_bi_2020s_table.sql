

WITH team_mapped AS (
SELECT d.full_name AS player_name,
       d.is_active,
       a.*,
        CASE WHEN EXTRACT(MONTH FROM a.game_timestamp) <= 7 THEN DATE_PART(YEAR, a.game_timestamp) - 1 ELSE DATE_PART(YEAR, a.game_timestamp) END AS YEAR_SEASON,
       b.abbreviation,
       b.city,
       b.state,
       b.year_founded,
       c.arena,
       c.arenacapacity,
       c.owner,
       c.headcoach,
       c.generalmanager,
       c.instagram AS instagram_link,
       c.facebook AS fb_link,
       c.twitter AS x_link,
FROM NBA_DB.REPORTS.player_all_time_stats_source a
JOIN NBA_DB.REPORTS.player_list_source d
       ON a.player_id = d.id
JOIN NBA_DB.REPORTS.team_list_source b ON a.player_team_id = b.id
LEFT JOIN NBA_DB.REPORTS.team_details_source c
       ON b.id = c.team_id
),
-- All of our player sources (list, details, career_accolades) we use to build the full end-user plofiles have conforming dimensions on the primary key PLAYER_ID --
player_profiles AS (
SELECT
    personid,
    birthdate,
    bodyweightlbs,
    heightinches,
    firstname,
    lastname,
    firstname || ' ' || lastname AS full_name,
    CASE WHEN TOYEAR > 2025 THEN 'ACTIVE' ELSE 'RETIRED' END AS is_active_player,
    school,
    fromyear,
    toyear,
    draftround,
    draftnumber,
    jersey,
    guard,
    forward,
    center
FROM NBA_DB.REPORTS.player_details_source
WHERE toyear >= 2021)

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

    FROM team_mapped a
        JOIN player_profiles b on a.player_id = b.personid
        WHERE a.YEAR_SEASON >= 2021
