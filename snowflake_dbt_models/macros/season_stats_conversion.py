{%- macro season_totals_to_per_season(stat_col, game_count, season, decimal_places = 2)-%}

for season in list(season):
{{ column_name }} / {{game_count}}


{%- endmacro -%}
