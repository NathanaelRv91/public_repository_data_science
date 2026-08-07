## CHECK my Semantic Layer Config before Uploading to @NBA_DB.REPORTS.NBA_STAGE/nba_semantic_models.yml
import yaml

with open("nba_stat_models_streamlit.yml", "r") as f:
    yaml.safe_load(f)

print("YAML is valid")
