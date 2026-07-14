{% snapshot snapshot_players %}

{{ config(target_schema = 'player_data',
strategy = 'check',
unique_key = 'player_id',
check_cols = ['is_retired','game_id'],
invalidate_hard_deletes = True
)}}

SELECT * FROM {{ref('player_game_data')}}


{% endsnapshot%}
