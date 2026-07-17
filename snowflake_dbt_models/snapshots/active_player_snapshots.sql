{% snapshot snapshot_players %}

{{ config(target_schema = 'player_data',
strategy = 'check',
unique_key = ['player_id','season_id'],
check_cols = ['is_active'],
invalidate_hard_deletes = True
)}}

SELECT * FROM {{ref('int_player_career_stats')}}

{% endsnapshot%}
