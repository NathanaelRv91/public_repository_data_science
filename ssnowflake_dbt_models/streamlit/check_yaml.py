import yaml

with open("nba_stat_models_streamlit.yml", "r") as f:
    yaml.safe_load(f)

print("YAML is valid")
