{%- macro season_totals_to_per_season(stat_col, game_count, season, decimal_places = 3)-%}
{% set seasons = [2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026] %}
  SELECT 
{% for {{season}} in seasons %}
    {{ stat_col }} / {{game_count}} AS {{season}}_{{stat_col}}
  {% end for %}
{%- endmacro -%}
